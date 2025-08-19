from flask import Blueprint, render_template, redirect, request, make_response, g, Response
import os
import json
import datetime
import requests
from openwrite.utils.models import Post, Blog, Home, Settings, Page, Like
from openwrite.routes.blog import create_person_object, is_activitypub_request
import time
from openwrite import start_time

from sqlalchemy import desc

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    if g.mode == "multi":
        langs = []
        home = g.db.query(Home).filter_by(name="hometext").all()
        for h in home:
            langs.append(h.language)
        return render_template('index.html', home=home, langs=langs)

    elif g.mode == "single":
        blog = g.db.query(Blog).filter_by(name="default").first()
        
        # Check for ActivityPub request
        if is_activitypub_request():
            blog_url = f"https://{g.main_domain}"
            person = create_person_object(blog, blog_url)
            return Response(json.dumps(person), content_type="application/activity+json", headers={
                'Cache-Control': 'max-age=3600',
                'Vary': 'Accept'
            })
        
        blog.url = f"http://{g.main_domain}"
        page = g.db.query(Page).filter_by(blog=blog.id, url="").first()
        pages = g.db.query(Page).filter_by(blog=blog.id).all()
        if '{posts}' in page.content_raw:
            posts = g.db.query(Post).filter_by(blog=blog.id).order_by(desc(Post.id)).all()
            return render_template('blog.html', blog=blog, page=page, posts=posts, pages=pages)
        posts = g.db.query(Post).filter_by(blog=blog.id).all()
        return render_template('blog.html', blog=blog, posts=posts, page=page, pages=pages)

@main_bp.route("/set-lang/<lang_code>")
def set_lang(lang_code):
    if lang_code not in g.alltrans:
        return redirect("/")
    resp = make_response(redirect(request.referrer or "/"))
    resp.set_cookie("lang", lang_code, max_age=60*60*24*365)
    return resp

@main_bp.route("/instances")
def instances():
    if g.mode == "single":
        return redirect("/")
    instances = ["https://openwrite.io"]  
    instances_data = []

    for i in instances:
        try:
            response = requests.get(f"{i}/.well-known/openwrite")
            response.raise_for_status()
            data = response.json()
            uptime = str(datetime.timedelta(seconds=data['uptime']))
            instances_data.append({
                "name": data['name'],
                "url": i,
                "users": data['users'],
                "uptime": uptime,
                "version": data['version'],
                "blogs": data['blogs'],
                "register": data['register'],
                "media": data['media']
            })
        except Exception:
            continue

    return render_template("instances.html", instances=instances_data)

@main_bp.route("/discover")
def discover():
    if g.mode == "single":
        return redirect("/")
    posts = g.db.query(Post).filter(Post.feed == "1", Post.isdraft == "0").order_by(desc(Post.id)).all()
    for p in posts:
        b = g.db.query(Blog).filter_by(id=p.blog).first()
        if not b:
            continue
        if b.access == "path":
            url = f"https://{os.getenv('DOMAIN')}/b/{b.name}/{p.link}"
        elif b.access == "domain":
            url = f"https://{b.name}.{os.getenv('DOMAIN')}/{p.link}"
        else:
            url = "#"
        l = g.db.query(Like).filter(Like.post == p.id, Like.blog == b.id).count()
        p.likes = l
        p.url = url
        p.blogname = b.title

    return render_template("discover.html", posts=posts)

@main_bp.route('/.well-known/openwrite')
def show_instance():
    from openwrite.utils.models import Blog, User 
    import time
    blog_count = g.db.query(Blog).count()
    user_count = g.db.query(User).count()
    return {
        "version": g.version,
        "blogs": blog_count,
        "users": user_count,
        "uptime": int(time.time() - int(start_time)),
        "name": os.getenv("DOMAIN"),
        "register": os.getenv("SELF_REGISTER"),
        "media": os.getenv("MEDIA_UPLOAD")
    }

