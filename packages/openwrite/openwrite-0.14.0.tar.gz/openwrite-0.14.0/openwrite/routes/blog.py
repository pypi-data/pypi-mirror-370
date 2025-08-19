from flask import Blueprint, render_template, redirect, request, g, Response, abort
from openwrite.utils.models import Blog, Post, User, View, Like, Page
from openwrite.utils.helpers import gen_link, sanitize_html, anonymize, get_ip
from openwrite.utils.valkey_client import valkey_client
from feedgen.feed import FeedGenerator
from sqlalchemy import desc
import os
import json
import re
from bs4 import BeautifulSoup
from datetime import timezone, datetime

blog_bp = Blueprint("blog", __name__)

def create_activity_object(post, blog, url, full_content=True):
    """Create ActivityPub object (Article or Note) based on post content length"""
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

def create_person_object(blog, url):
    """Create ActivityPub Person object for the blog"""
    published = blog.created
    dt = datetime.strptime(str(published), "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=timezone.utc)
    iso = dt.isoformat(timespec="seconds").replace("+00:00", "Z")
    if blog.fedi_description != "":
        summary = blog.fedi_description
    else:
        summary = f"{blog.name} - Blog on {g.main_domain}"

    actor = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {
                "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
                "discoverable": "as:discoverable",
                "indexable": "as:indexable"
            }
        ],
        "id": url,
        "type": "Person",
        "preferredUsername": blog.name,
        "name": blog.title,
        "summary": summary,
        "inbox": f"https://{g.main_domain}/inbox/{blog.name}",
        "outbox": f"https://{g.main_domain}/outbox/{blog.name}",
        "followers": f"https://{g.main_domain}/followers/{blog.name}",
        "published": iso,
        "manuallyApprovesFollowers": False,
        "discoverable": True,
        "indexable": True,
        "url": url,
        "attachment": [
            {
            "type": "PropertyValue",
            "name": "Blog",
            "value": f"<a href=\"{url}\" target=\"_blank\" rel=\"nofollow noopener noreferrer me\" translate=\"no\"><span class=\"\">{url}</span><span class=\"invisible\"></span></a>"
            }
        ],
        "publicKey": {
            "id": f"{url}#main-key",
            "owner": url,
            "publicKeyPem": blog.pub_key
        },
        "icon": {
            "type": "Image",
            "mediaType": "image/png",
            "url": f"https://{g.main_domain}/static/avatar.png"
        }
    }
    return actor

def is_activitypub_request():
    """Check if the request is asking for ActivityPub content"""
    accept = request.headers.get('Accept', '')
    return 'application/activity+json' in accept or 'application/ld+json' in accept or 'application/json' in accept

@blog_bp.route("/b/<blog>")
def show_blog(blog):
    if g.mode == "single":
        return redirect("/")
    blog_obj = g.db.query(Blog).filter_by(name=blog).first()
    if blog_obj is None:
        return redirect("/")

    if blog_obj.access == "domain":
        return redirect(f"https://{blog_obj.name}.{os.getenv('DOMAIN')}/")

    if is_activitypub_request():
        url = f"https://{g.main_domain}/b/{blog}"
        person = create_person_object(blog_obj, url)
        return Response(json.dumps(person), content_type="application/activity+json", headers={
            'Cache-Control': 'max-age=3600',
            'Vary': 'Accept'
        })

    pages = g.db.query(Page).filter_by(blog=blog_obj.id).all()
    blog_obj.url = f"/b/{blog_obj.name}"
    homepage = g.db.query(Page).filter(Page.blog == blog_obj.id, Page.url == "").first()
    if "{posts}" in homepage.content_raw:
        posts = g.db.query(Post).filter(Post.blog == blog_obj.id, Post.isdraft == "0").order_by(desc(Post.id)).all()
        return render_template("blog.html", blog=blog_obj, page=homepage, posts=posts, pages=pages)

    return render_template("blog.html", blog=blog_obj, page=homepage, pages=pages)

@blog_bp.route("/", subdomain="<blog>")
def show_subblog(blog):
    if g.mode == "single":
        return redirect("/")
    blog_obj = g.db.query(Blog).filter_by(name=blog).first()
    if blog_obj is None:
        return redirect(f"https://{os.getenv('DOMAIN')}/")

    if blog_obj.access == "path":
        return redirect(f"https://{os.getenv('DOMAIN')}/b/{blog_obj.name}")

    if is_activitypub_request():
        url = f"https://{blog}.{g.main_domain}"
        person = create_person_object(blog_obj, url)
        return Response(json.dumps(person), content_type="application/activity+json", headers={
            'Cache-Control': 'max-age=3600',
            'Vary': 'Accept'
        })

    blog_obj.url = f"https://{blog_obj.name}.{os.getenv('DOMAIN')}"
    pages = g.db.query(Page).filter_by(blog=blog_obj.id).all()
    homepage = g.db.query(Page).filter(Page.blog == blog_obj.id, Page.url == "").first()
    if "{posts}" in homepage.content_raw:
        posts = g.db.query(Post).filter(Post.blog == blog_obj.id, Post.isdraft == "0").order_by(desc(Post.id)).all()
        return render_template("blog.html", blog=blog_obj, page=homepage, posts=posts, pages=pages)

    return render_template("blog.html", blog=blog_obj, page=homepage, pages=pages)

@blog_bp.route("/b/<blog>/<post>")
def show_post(blog, post):
    if g.mode == "single":
        return redirect("/")
    blog_obj = g.db.query(Blog).filter_by(name=blog).first()
    if blog_obj is None:
        return redirect("/")

    if post == "rss":
        return _generate_rss(blog_obj)

    if blog_obj.access == "domain":
        return redirect(f"https://{blog_obj.name}.{os.getenv('DOMAIN')}/{post}")

    blog_obj.url = f"/b/{blog_obj.name}"
    pages = g.db.query(Page).filter_by(blog=blog_obj.id).all()
    one_post = g.db.query(Post).filter(Post.blog == blog_obj.id, Post.link == post, Post.isdraft == "0").first()
    
    if not one_post:
        page = g.db.query(Page).filter(Page.blog == blog_obj.id, Page.url == post).first()
        if not page:
            return redirect("/")

        if "{posts}" in page.content_raw:
            posts = g.db.query(Post).filter(Post.blog == blog_obj.id, Post.isdraft == "0").order_by(desc(Post.id)).all()
            return render_template("blog.html", blog=blog_obj, page=page, posts=posts, pages=pages)
        
        return render_template("blog.html", blog=blog_obj, page=page, pages=pages)

    if is_activitypub_request():
        url = f"https://{g.main_domain}/b/{blog}"
        activity_obj = create_activity_object(one_post, blog, url)
        activity_obj["@context"] = "https://www.w3.org/ns/activitystreams"
        return Response(json.dumps(activity_obj), content_type="application/activity+json", headers={
            'Cache-Control': 'max-age=3600',
            'Vary': 'Accept'
        })

    post_author = g.db.query(User).filter_by(id=blog_obj.owner).first()
    one_post.authorname = post_author.username
    blog_obj.url = f"/b/{blog_obj.name}"

    user_agent = request.headers.get('User-Agent')
    ip = anonymize(get_ip())

    if 'Bot' not in user_agent:
        v = g.db.query(View).filter(View.blog == blog_obj.id, View.post == one_post.id, View.hash == ip).count()
        if v < 1:
            if valkey_client.is_enabled():
                valkey_client.queue_view(blog_obj.id, one_post.id, ip, user_agent)
            else:
                now = datetime.now(timezone.utc).replace(microsecond=0)
                new_view = View(blog=blog_obj.id, post=one_post.id, hash=ip, date=now, agent=user_agent)
                g.db.add(new_view)
                g.db.commit()

    likes_db = g.db.query(Like).filter(Like.blog == blog_obj.id, Like.post == one_post.id).count()
    likes_queued = valkey_client.count_queued_likes(blog_obj.id, one_post.id) if valkey_client.is_enabled() else 0
    likes = likes_db + likes_queued

    liked_db = g.db.query(Like).filter(Like.blog == blog_obj.id, Like.post == one_post.id, Like.hash == ip).count()
    liked_queued = valkey_client.check_queued_like(blog_obj.id, one_post.id, ip) if valkey_client.is_enabled() else False
    liked = liked_db or liked_queued

    one_post.likes = likes
    one_post.liked = liked

    user = g.db.query(User).filter_by(id=g.user) if g.user else None
    return render_template("post.html", blog=blog_obj, post=one_post, user=user, views=v, likes=likes, pages=pages)

@blog_bp.route("/<post>", subdomain="<blog>")
def show_subpost(blog, post):
    if g.mode == "single":
        return redirect("/")
    blog_obj = g.db.query(Blog).filter_by(name=blog).first()
    if blog_obj is None:
        return redirect(f"https://{os.getenv('DOMAIN')}/")

    if post == "rss":
        return _generate_rss(blog_obj)

    if blog_obj.access == "path":
        return redirect(f"https://{os.getenv('DOMAIN')}/b/{blog_obj.name}/{post}")

    blog_obj.url = f"https://{blog_obj.name}.{os.getenv('DOMAIN')}"

    pages = g.db.query(Page).filter_by(blog=blog_obj.id).all()
    one_post = g.db.query(Post).filter(Post.blog == blog_obj.id, Post.link == post, Post.isdraft == "0").first()

    if not one_post:
        page = g.db.query(Page).filter(Page.blog == blog_obj.id, Page.url == post).first()
        if not page:
            return redirect("/")

        if "{posts}" in page.content_raw:
            posts = g.db.query(Post).filter(Post.blog == blog_obj.id, Post.isdraft == "0").order_by(desc(Post.id)).all()
            return render_template("blog.html", blog=blog_obj, page=page, posts=posts, pages=pages)
        
        return render_template("blog.html", blog=blog_obj, page=page, pages=pages)

    if is_activitypub_request():
        url = f"https://{blog}.{g.main_domain}"
        activity_obj = create_activity_object(one_post, blog, url)
        activity_obj["@context"] = "https://www.w3.org/ns/activitystreams"
        return Response(json.dumps(activity_obj), content_type="application/activity+json", headers={
            'Cache-Control': 'max-age=3600',
            'Vary': 'Accept'
        })

    post_author = g.db.query(User).filter_by(id=blog_obj.owner).first()
    one_post.authorname = post_author.username
    blog_obj.url = f"https://{blog_obj.name}.{os.getenv('DOMAIN')}"

    user_agent = request.headers.get('User-Agent')
    ip = anonymize(get_ip())

    if 'Bot' not in user_agent:
        v = g.db.query(View).filter(View.blog == blog_obj.id, View.post == one_post.id, View.hash == ip).count()
        if v < 1:
            if valkey_client.is_enabled():
                valkey_client.queue_view(blog_obj.id, one_post.id, ip, user_agent)
            else:
                now = datetime.now(timezone.utc).replace(microsecond=0)
                new_view = View(blog=blog_obj.id, post=one_post.id, hash=ip, date=now, agent=user_agent)
                g.db.add(new_view)
                g.db.commit()

    likes_db = g.db.query(Like).filter(Like.blog == blog_obj.id, Like.post == one_post.id).count()
    likes_queued = valkey_client.count_queued_likes(blog_obj.id, one_post.id) if valkey_client.is_enabled() else 0
    likes = likes_db + likes_queued

    liked_db = g.db.query(Like).filter(Like.blog == blog_obj.id, Like.post == one_post.id, Like.hash == ip).count()
    liked_queued = valkey_client.check_queued_like(blog_obj.id, one_post.id, ip) if valkey_client.is_enabled() else False
    liked = liked_db or liked_queued

    one_post.likes = likes
    one_post.liked = liked

    user = g.db.query(User).filter_by(id=g.user) if g.user else None
    return render_template("post.html", blog=blog_obj, post=one_post, user=user, views=v, likes=likes, pages=pages)

@blog_bp.route("/.well-known/webfinger")
def webfinger():
    resource = request.args.get("resource")
    if not resource or not resource.startswith("acct:"):
        abort(400)

    account_part = resource.split(":")[1]
    if "@" not in account_part:
        abort(400)
        
    username, domain = account_part.split("@", 1)
    
    blog_obj = g.db.query(Blog).filter_by(name=username).first()
    if not blog_obj:
        abort(404)
    
    if blog_obj.access == "domain":
        blog_url = f"https://{username}.{g.main_domain}"
    else:
        blog_url = f"https://{g.main_domain}/b/{username}"
    
    data = {
        "subject": f"acct:{username}@{g.main_domain}",
        "links": [{
            "rel": "self",
            "type": "application/activity+json",
            "href": blog_url
        }]
    }

    return Response(
        response=json.dumps(data),
        status=200,
        content_type="application/jrd+json"
    )

@blog_bp.route("/.well-known/webfinger", subdomain="<blog>")
def subdomain_webfinger(blog):
    """Redirect subdomain webfinger requests to main domain"""
    resource = request.args.get("resource")
    if not resource:
        abort(400)
    
    if resource.startswith("acct:"):
        account_part = resource.split(":")[1]
        if "@" in account_part:
            username = account_part.split("@")[0]
            corrected_resource = f"acct:{username}@{g.main_domain}"
            return redirect(f"https://{g.main_domain}/.well-known/webfinger?resource={corrected_resource}")
    
    return redirect(f"https://{g.main_domain}/.well-known/webfinger?resource={resource}")

@blog_bp.route("/p/<post>")
def single_showpost(post):
    if g.mode == "multi":
        return redirect("/")

    blog = g.db.query(Blog).filter_by(id=1).first()
    blog.url = f"http://{g.main_domain}"
    one_post = g.db.query(Post).filter(Post.blog == 1, Post.link == post, Post.isdraft == "0").first()

    pages = g.db.query(Page).filter_by(blog=1).all()

    if not one_post:
        page = g.db.query(Page).filter(Page.blog == blog.id, Page.url == post).first()
        if not page:
            return redirect("/")

        if "{posts}" in page.content_raw:
            posts = g.db.query(Post).filter(Post.blog == blog.id, Post.isdraft == "0").order_by(desc(Post.id)).all()

            return render_template("blog.html", blog=blog, page=page, posts=posts, pages=pages)
        
        return render_template("blog.html", blog=blog, page=page, pages=pages)

    if is_activitypub_request():
        url = f"https://{g.main_domain}"
        activity_obj = create_activity_object(one_post, "default", url)
        activity_obj["@context"] = "https://www.w3.org/ns/activitystreams"
        return Response(json.dumps(activity_obj), content_type="application/activity+json", headers={
            'Cache-Control': 'max-age=3600',
            'Vary': 'Accept'
        })

    post_author = g.db.query(User).filter_by(id=1).first()
    one_post.authorname = post_author.username

    user_agent = request.headers.get('User-Agent', '')
    ip = anonymize(get_ip())

    if 'Bot' not in user_agent:
        v = g.db.query(View).filter(View.blog == blog.id, View.post == one_post.id, View.hash == ip).count()
        if v < 1:
            if valkey_client.is_enabled():
                valkey_client.queue_view(blog.id, one_post.id, ip, user_agent)
            else:
                now = datetime.now(timezone.utc).replace(microsecond=0)
                new_view = View(blog=blog.id, post=one_post.id, hash=ip, date=now, agent=user_agent)
                g.db.add(new_view)
                g.db.commit()

    likes_db = g.db.query(Like).filter(Like.blog == blog.id, Like.post == one_post.id).count()
    likes_queued = valkey_client.count_queued_likes(blog.id, one_post.id) if valkey_client.is_enabled() else 0
    likes = likes_db + likes_queued

    liked_db = g.db.query(Like).filter(Like.blog == blog.id, Like.post == one_post.id, Like.hash == ip).count()
    liked_queued = valkey_client.check_queued_like(blog.id, one_post.id, ip) if valkey_client.is_enabled() else False
    liked = liked_db or liked_queued

    one_post.likes = likes
    one_post.liked = liked

    user = g.db.query(User).filter_by(id=g.user) if g.user else None
    return render_template("post.html", blog=blog, post=one_post, user=user, views=v, likes=likes, pages=pages)

@blog_bp.route("/rss")
def single_rss():
    if g.mode == "multi":
        return redirect("/")

    blog = g.db.query(Blog).first()
    return _generate_rss(blog)

@blog_bp.route("/like", methods=["POST"])
def like():
    data = request.get_json()
    if not data:
        abort(400)
    
    blog_id = data.get("blog")
    post_id = data.get("post")
    post = g.db.query(Post).filter(Post.blog == blog_id, Post.id == post_id).count()
    if post < 1:
        resp = {"status": "no_post"}
        return resp, 404
    
    ip = anonymize(get_ip())

    liked_db = g.db.query(Like).filter(Like.blog == blog_id, Like.post == post_id, Like.hash == ip).first()
    liked_queued = valkey_client.check_queued_like(blog_id, post_id, ip) if valkey_client.is_enabled() else False

    if liked_db:
        if liked_db and valkey_client.is_enabled():
            valkey_client.queue_like(blog_id, post_id, ip, 'remove')
        elif liked_db and not valkey_client.is_enabled():
            g.db.delete(liked_db)
            g.db.commit()

        resp = {"status": "deleted"}
        status = 204

    elif liked_queued and valkey_client.is_enabled():
        valkey_client.queue_like(blog_id, post_id, ip, 'remove')
        
        resp = {"status": "deleted"}
        status = 204
    else:
        if valkey_client.is_enabled():
            valkey_client.queue_like(blog_id, post_id, ip, 'add')
        else:
            now = datetime.now(timezone.utc).replace(microsecond=0)
            like = Like(blog=blog_id, post=post_id, hash=ip, date=now)
            g.db.add(like)
            g.db.commit()
        
        resp = {"status": "ok"}
        status = 201
    
    return resp, status
    

def _generate_rss(blog):
    posts = g.db.query(Post).filter(Post.blog == blog.id, Post.isdraft == "0").all()
    fg = FeedGenerator()
    fg.title(blog.title)
    
    if blog.access == "domain":
        blog_url = f"https://{blog.name}.{g.main_domain}"
        post_base_url = blog_url
    else:
        blog_url = f"https://{g.main_domain}/b/{blog.name}"
        post_base_url = blog_url
    
    fg.link(href=blog_url, rel="alternate")
    fg.description(blog.description_html)

    for p in posts:
        soup = BeautifulSoup(p.content_html, "html.parser")
        fe = fg.add_entry()
        fe.title(p.title)
        fe.link(href=f"{post_base_url}/{p.link}")
        fe.description(soup.get_text())
        fe.published(p.date.replace(tzinfo=timezone.utc))

    return Response(fg.rss_str(pretty=True).decode("utf-8"), mimetype="application/rss+xml")