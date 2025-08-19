from flask import Blueprint, render_template, redirect, g, jsonify, request, abort, Response
from openwrite.utils.models import Blog, User, Like, Post
from openwrite.utils.helpers import verify_http_signature, send_activity, anonymize
import json
import requests
from datetime import datetime, timezone, timedelta
import re

federation_bp = Blueprint("federation", __name__)

def create_activity_object(post, blog, url, full_content=True):
    dt = datetime.strptime(str(post.date), "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=timezone.utc)
    iso = dt.isoformat(timespec="seconds").replace("+00:00", "Z")
    
    clean_content = re.sub(r'<[^>]+>', '', post.content_html)
    content_length = len(clean_content)
    
    base_object = {
        "id": f"{url}/{post.link}",
        "attributedTo": url,
        "published": iso,
        "url": f"{url}/{post.link}",
        "to": ["https://www.w3.org/ns/activitystreams#Public"],
        "cc": [f"https://{g.main_domain}/followers/{blog}"],
        "sensitive": False,
        "atomUri": f"{url}/{post.link}",
        "attachment": [],
        "tag": []
    }
    
    if content_length > 200:
        words = clean_content.split()[:50]
        summary = ' '.join(words) + '...' if len(words) == 50 else ' '.join(words)
        
        if full_content:
            content = f"<h1>{post.title}</h1>{post.content_html}"
        else:
            content = f"<p><a href=\"{url}/{post.link}\">Read full article: {post.title}</a></p>"
        
        base_object.update({
            "type": "Article",
            "name": post.title,
            "summary": summary,
            "content": content
        })
    else:
        base_object.update({
            "type": "Note",
            "summary": None,
            "content": f"<h3>{post.title}</h3>{post.content_html}<p><a href=\"{url}/{post.link}\">View post</a></p>"
        })
    
    return base_object

@federation_bp.route("/inbox/<blog>", methods=["POST"])
def inbox(blog):
    b = g.db.query(Blog).filter_by(name=blog).first()
    if not b:
        abort(404)

    data = request.get_json()
    if not data:
        return "Bad Request", 400

    body = request.get_data(as_text=True)
    sign = verify_http_signature(request.headers, body, blog)
    if not sign:
        return "Bad signature", 400
    
    if b.access == "path":
        blog_url = f"https://{g.main_domain}/b/{blog}"
    else:
        blog_url = f"https://{blog}.{g.main_domain}"
    
    if data.get("type") == "Follow":
        actor = data.get("actor")
        object_ = data.get("object")
        id_ = data.get("id")

        if object_ != blog_url:
            return "Invalid target", 400

        followers = []
        if b.followers not in (None, "null", "NULL"):
            followers = json.loads(b.followers)
        if actor not in followers:
            followers.append(actor)
        b.followers = json.dumps(followers)
        g.db.commit()

        activity = {
          "@context": "https://www.w3.org/ns/activitystreams",
          "id": f"{blog_url}#accept-{id_.split('/')[-1]}",
          "type": "Accept",
          "actor": blog_url,
          "object": data,
          "to": [f"{actor}"]
        }
        
        actor_doc = requests.get(actor, headers={"Accept": "application/activity+json"}).json()
        inbox = actor_doc.get("endpoints", {}).get("sharedInbox", actor)

        send_activity(activity, b.priv_key, blog_url, f"{actor}/inbox")

        return "", 202

    elif data.get("type") == "Undo":
        actor = data.get("actor")
        object_ = data.get("object")
        
        if object_['type'] == "Follow":
            if object_['object'] != blog_url:
                return "Invalid target", 400

            followers = []
            if b.followers not in (None, "null", "NULL"):
                followers = json.loads(b.followers)
            if actor in followers:
                followers.remove(actor)
            b.followers = json.dumps(followers)
            g.db.commit()

        elif object_['type'] == "Like":
            post_name = object_['object'].split("/")[-1]
            if object_['object'].split("/")[2] == g.main_domain:
                blog_name = object_['object'].split("/")[-2]
            else:
                blog_name = object_['object'].split("/")[2].split('.')[0]
            blog_obj = g.db.query(Blog).filter_by(name=blog_name).first()
            blog_id = blog_obj.id
            post = g.db.query(Post).filter(Post.blog == blog_id, Post.link == post_name).first()
            post_id = post.id

            hashed = anonymize(actor)
            like = g.db.query(Like).filter(Like.blog == blog_id, Like.post == post_id, Like.hash == hashed).first()
            g.db.delete(like)
            g.db.commit()
        
        return "", 202

    elif data.get("type") == "Like":
        object_ = data.get("object")
        actor = data.get("actor")
        post_name = object_.split("/")[-1]
        if object_.split("/")[2] == g.main_domain:
            blog_name = object_.split("/")[-2]
        else:
            blog_name = object_.split("/")[2].split('.')[0]
        blog_obj = g.db.query(Blog).filter_by(name=blog_name).first()
        blog_id = blog_obj.id
        post = g.db.query(Post).filter(Post.blog == blog_id, Post.link == post_name).first()
        post_id = post.id

        hashed = anonymize(actor)
        like = Like(hash=hashed, blog=blog_id, post=post_id)
        g.db.add(like)
        g.db.commit()

    return "", 202

@federation_bp.route("/outbox/<blog>")
def outbox(blog):
    page = request.args.get("page")
    
    b = g.db.query(Blog).filter_by(name=blog).first()
    if not b:
        abort(404)

    p = g.db.query(Post).filter(Post.blog == b.id, Post.isdraft == "0").order_by(Post.date.desc())
    total = p.count()
    posts = p.all()
    
    first_outbox = {
      "@context": "https://www.w3.org/ns/activitystreams",
      "id": f"https://{g.main_domain}/outbox/{blog}",
      "type": "OrderedCollection",
      "totalItems": total,
      "first": f"https://{g.main_domain}/outbox/{blog}?page=true"
    }

    if not page:
        if total <= 10:
            orderedPosts = []
            if b.access == "path":
                url = f"https://{g.main_domain}/b/{blog}"
            else:
                url = f"https://{blog}.{g.main_domain}"
            
            for post in posts:
                dt = datetime.strptime(str(post.date), "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=timezone.utc)
                iso = dt.isoformat(timespec="seconds").replace("+00:00", "Z")   
                orderedPosts.append({
                    "id": f"{url}/create/{post.id}",
                    "type": "Create",
                    "actor": url,
                    "published": iso,
                    "to": ["https://www.w3.org/ns/activitystreams#Public"],
                    "cc": [f"https://{g.main_domain}/followers/{blog}"],
                    "object": create_activity_object(post, blog, url, full_content=False)
                })
            
            first_outbox["orderedItems"] = orderedPosts
            
            return Response(json.dumps(first_outbox), content_type="application/activity+json; charset=utf-8", headers={
                'Cache-Control': 'max-age=300',
                'Vary': 'Accept'
            })
        else:
            return Response(json.dumps(first_outbox), content_type="application/activity+json; charset=utf-8", headers={
                'Cache-Control': 'max-age=300',
                'Vary': 'Accept'
            })

    orderedPosts = []
    if b.access == "path":
        url = f"https://{g.main_domain}/b/{blog}"
    else:
        url = f"https://{blog}.{g.main_domain}"
    for post in posts:
        dt = datetime.strptime(str(post.date), "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=timezone.utc)
        iso = dt.isoformat(timespec="seconds").replace("+00:00", "Z")   
        orderedPosts.append({
            "id": f"{url}/create/{post.id}",
            "type": "Create",
            "actor": url,
            "published": iso,
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [f"https://{g.main_domain}/followers/{blog}"],
            "object": create_activity_object(post, blog, url, full_content=False)
        })

    outbox = {
      "@context": [
        "https://www.w3.org/ns/activitystreams",
        {
          "ostatus": "http://ostatus.org#",
          "atomUri": "ostatus:atomUri",
          "inReplyToAtomUri": "ostatus:inReplyToAtomUri",
          "conversation": "ostatus:conversation",
          "sensitive": "as:sensitive",
          "toot": "http://joinmastodon.org/ns#",
          "votersCount": "toot:votersCount"
        }
      ],
      "id": f"https://{g.main_domain}/outbox/{blog}?page={page}",
      "type": "OrderedCollectionPage",
      "partOf": f"https://{g.main_domain}/outbox/{blog}",
      "orderedItems": orderedPosts
    }

    return Response(json.dumps(outbox), content_type="application/activity+json", headers={
        'Cache-Control': 'max-age=300',
        'Vary': 'Accept'
    })

@federation_bp.route("/followers/<blog>")
def followers(blog):
    page = request.args.get("page")
    b = g.db.query(Blog).filter_by(name=blog).first()
    if not b:
        abort(404)

    followers = []
    if b.followers not in (None, "null", "NULL"):
        followers = json.loads(b.followers)

    if page not in ("true", "1"):
        data = {
          "@context": "https://www.w3.org/ns/activitystreams",
          "id": f"https://{g.main_domain}/followers/{blog}",
          "type": "OrderedCollection",
          "totalItems": len(followers),
          "first": {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"https://{g.main_domain}/followers/{blog}?page=true",
            "type": "OrderedCollectionPage",
            "partOf": f"https://{g.main_domain}/followers/{blog}",
            "totalItems": len(followers),
            "orderedItems": followers
          }
        }

        return Response(json.dumps(data), content_type="application/activity+json")

    data = {
      "@context": "https://www.w3.org/ns/activitystreams",
      "id": f"https://{g.main_domain}/followers/{blog}?page={page}",
      "type": "OrderedCollectionPage",
      "totalItems": len(followers),
      "partOf": f"https://{g.main_domain}/followers/{blog}",
      "orderedItems": followers
    }

    return Response(json.dumps(data), content_type="application/activity+json")

@federation_bp.route("/nodeinfo/2.0")
@federation_bp.route("/nodeinfo/2.0.json")
@federation_bp.route("/.well-known/nodeinfo")
def nodeinfo():
    data = {
        "version": "2.0",
        "software": {
            "name": "OpenWrite",
            "version": g.version,
        },
        "protocols": ["activitypub"],
        "services": {
            "outbound": [],
            "inbound": []
        },
        "usage": {
            "users": {
                "total": g.db.query(User).count(),
                "activeMonth": g.db.query(Post).filter(Post.updated >= datetime.now(timezone.utc) - timedelta(days=30)).count(),
                "activeHalfyear": g.db.query(Post).filter(Post.updated >= datetime.now(timezone.utc) - timedelta(days=180)).count()
            },
            "localPosts": g.db.query(Post).count()
        },
        "openRegistrations": True,
        "metadata": {
            "nodeName": "OpenWrite Node",
            "nodeDescription": "Federated blogging platform supporting ActivityPub, allowing users to create and share posts across different instances."
        }
    }

    return jsonify(data), 200, {'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'max-age=3600'}