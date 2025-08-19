from flask import Blueprint, render_template, redirect, request, g, abort, Response
from openwrite.utils.models import Blog, Post, User, View, Like, Page
from openwrite.utils.helpers import sanitize_html, gen_link, safe_css, send_activity, is_html, get_themes
from openwrite.routes.blog import create_activity_object, create_person_object
from openwrite.utils.valkey_client import valkey_client
import requests
from sqlalchemy import desc
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import json
import bcrypt
import markdown
from bs4 import BeautifulSoup
from user_agents import parse
import re
import csv
from io import StringIO

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if g.user is None:
        return redirect("/login")

    user_blogs = g.db.query(Blog).filter_by(owner=g.user).all()
    user = g.db.query(User).filter_by(id=g.user)

    return render_template("dashboard.html", blogs=user_blogs, user=user)

@dashboard_bp.route("/dashboard/create", methods=['GET', 'POST'])
def create_blog():
    if g.mode == "single":
        return redirect("/")
    if g.user is None:
        return redirect("/login")

    if int(g.blog_limit) > 0:
        count = g.db.query(Blog).filter_by(owner=g.user).count()
        if count >= int(g.blog_limit):
            return render_template("create.html", error="blog-limit-reached")

    if request.method == "GET":
        return render_template("create.html")

    form_name = request.form.get("name")
    form_url = gen_link(request.form.get("url"))
    if len(form_name) > 30:
        return render_template("create.html", error="title-too-long")
    if len(form_url) > 30:
        return render_template("create.html", error="url-too-long")
    blog = g.db.query(Blog).filter_by(name=form_url).first()
    if blog:
        return render_template("create.html", error="url-exists")
    
    form_index = request.form.get("index") or "off"
    form_access = request.form.get("access")
    if form_access not in ("path", "domain"):
        return render_template("create.html", error="wrong-access")
    
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        new_blog = Blog(
            owner=g.user,
            title=form_name,
            name=form_url,
            index=form_index,
            access=form_access,
            css="",
            description_raw="x",
            description_html="x",
            fedi_description=f"{form_name} - Blog on {g.main_domain}",
            pub_key=public_pem,
            priv_key=private_pem,
            theme="default",
            favicon="",
            created=now
        )
        g.db.add(new_blog)
        g.db.commit()

        b_id = g.db.query(Blog).filter_by(name=form_url).first().id

        new_page = Page(
            blog=b_id,
            name="Home",
            url="",
            content_raw=f"![hello](https://openwrite.b-cdn.net/hello.jpg =500x258)\n\n# Hello there! 👋\n\nYou can edit your blog home page in [dashboard](https://{g.main_domain}/dashboard/edit/{form_url})\n\n---\n### Posts\n\n{{posts}}",
            content_html=f"<p><img src=\"https://openwrite.b-cdn.net/hello.jpg\" width=\"500\" height=\"258\"></p><h1>Hello there! 👋</h1><p>You can edit your blog home page in <a href=\"https://{g.main_domain}/dashboard/edit/{form_url}\">dashboard</a></p>\n\n<hr>\n<h3>Posts</h3>\n\n{{posts}}",
            show="0"
        )
        g.db.add(new_page)
        g.db.commit()
           
        return redirect("/dashboard")
    except Exception:
        return render_template("create.html", error="error")

@dashboard_bp.route("/dashboard/delete/<name>")
def delete_blog(name):
    if g.mode == "single":
        return redirect("/")
    if g.user is None:
        return redirect("/login")

    blog = g.db.query(Blog).filter_by(name=name).first()
    if blog is None or blog.owner != g.user:
        abort(403)

    if blog.access == "domain":
        blog_url = f"https://{blog.name}.{g.main_domain}"
    else:
        blog_url = f"https://{g.main_domain}/b/{blog.name}"

    followers = []
    if blog.followers not in (None, "null", "NULL"):
        followers = json.loads(blog.followers)

    if followers:
        person_object = create_person_object(blog, blog_url)
        
        for actor in followers:
            now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            delete_activity = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{blog_url}#delete-{now_iso}",
                "type": "Delete",
                "actor": blog_url,
                "published": now_iso,
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": [f"https://{g.main_domain}/followers/{blog.name}"],
                "object": person_object
            }
            if valkey_client.is_enabled():
                valkey_client.queue_federation_activity(delete_activity, blog.id, blog.priv_key, blog_url, f"{actor}/inbox")
            else:
                send_activity(delete_activity, blog.priv_key, blog_url, f"{actor}/inbox")

    g.db.delete(blog)
    g.db.commit()
    return redirect("/dashboard")

@dashboard_bp.route("/dashboard/edit/<name>", methods=['GET', 'POST'])
def edit_blog(name):
    if g.user is None:
        return redirect("/login")

    blog = g.db.query(Blog).filter_by(name=name).first()
    if blog is None or blog.owner != g.user:
        abort(403)

    posts = g.db.query(Post).filter_by(blog=blog.id).all()
    for p in posts:
        v = g.db.query(View).filter(View.post == p.id, View.blog == blog.id).count()
        p.views = v

    pages = g.db.query(Page).filter_by(blog=blog.id).all()

    themes = get_themes()
    themes.append("default")

    if request.method == "GET":
        return render_template("edit.html", blog=blog, posts=posts, themes=themes, pages=pages)

    now = datetime.now(timezone.utc).replace(microsecond=0)
    if len(request.form.get("title")) > 30:
        return render_template("edit.html", blog=blog, posts=posts, themes=themes, pages=pages, error="title-too-long")
    
    old_title = blog.title
    old_fedi_description = blog.fedi_description
    new_title = request.form.get("title")
    new_fedi_description = request.form.get("fedi_description", "")
    
    blog.css = safe_css(request.form.get("css"))
    blog.fedi_description = new_fedi_description
    blog.updated = now   
    blog.title = new_title
    blog.favicon = request.form.get("icon")[:10]
    selected_theme = request.form.get("theme")
    if selected_theme not in themes:
        return render_template("edit.html", blog=blog, posts=posts, themes=themes, pages=pages, error="wrong-theme")
    blog.theme = selected_theme
    g.db.commit()

    if old_title != new_title or old_fedi_description != new_fedi_description:
        if blog.access == "domain":
            blog_url = f"https://{blog.name}.{g.main_domain}"
        else:
            blog_url = f"https://{g.main_domain}/b/{blog.name}"

        followers = []
        if blog.followers not in (None, "null", "NULL"):
            followers = json.loads(blog.followers)

        if followers:
            person_object = create_person_object(blog, blog_url)
            
            for actor in followers:
                now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                update_activity = {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "id": f"{blog_url}#update-{now_iso}",
                    "type": "Update",
                    "actor": blog_url,
                    "published": now_iso,
                    "to": ["https://www.w3.org/ns/activitystreams#Public"],
                    "cc": [f"https://{g.main_domain}/followers/{blog.name}"],
                    "object": person_object
                }
                if valkey_client.is_enabled():
                    valkey_client.queue_federation_activity(update_activity, blog.id, blog.priv_key, blog_url, f"{actor}/inbox")
                else:
                    send_activity(update_activity, blog.priv_key, blog_url, f"{actor}/inbox")

    return render_template("edit.html", blog=blog, posts=posts, themes=themes, pages=pages)


@dashboard_bp.route("/dashboard/post/<name>", methods=['GET', 'POST'])
def new_post(name):
    if g.user is None:
        return redirect("/login")

    blog = g.db.query(Blog).filter_by(name=name).first()
    if blog is None or blog.owner != g.user:
        abort(403)

    if request.method == "GET":
        return render_template("new_post.html", blog=blog)

    u = g.db.query(User).filter_by(id=g.user).first()
    title = request.form.get('title')
    if len(title) > 120:
        return render_template("new_post.html", blog=blog, error="title-too-long")

    if len(title) < 1:
        return render_template("new_post.html", blog=blog, error="title-empty")

    link = gen_link(title)
    if link == "rss":
        link = "p_rss"
    dupes_posts = g.db.query(Post).filter(Post.link.startswith(link), Post.blog == blog.id).count()
    dupes_pages = g.db.query(Page).filter(Page.url == link, Page.blog == blog.id).count()
    dupes = dupes_posts + dupes_pages
    if dupes > 0:
        link += f"-{dupes + 1}"

    now = datetime.now(timezone.utc).replace(microsecond=0)
    date = now

    post = Post(
        blog=blog.id,
        title=title,
        content_raw=request.form.get('content_raw'),
        content_html=sanitize_html(request.form.get('content')),
        author=request.form.get('author'),
        link=link,
        date=now,
        feed=request.form.get('feed'),
        isdraft=request.form.get('draft', '0')
    )
    g.db.add(post)
    g.db.commit()
    
    if blog.access == "domain":
        blog_url = f"https://{blog.name}.{g.main_domain}"
    else:
        blog_url = f"https://{g.main_domain}/b/{blog.name}"

    followers = []
    if blog.followers not in (None, "null", "NULL"):
        followers = json.loads(blog.followers)

    if followers:
        if request.form.get("draft", "0") == "0":
            activity_object = create_activity_object(post, blog.name, blog_url, full_content=False)
            
            for actor in followers:
                now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                activity = {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "id": f"{blog_url}/{post.link}#create",
                    "type": "Create",
                    "actor": blog_url,
                    "published": now_iso,
                    "to": ["https://www.w3.org/ns/activitystreams#Public"],
                    "cc": [f"https://{g.main_domain}/followers/{blog.name}"],
                    "object": activity_object
                }       
                if valkey_client.is_enabled():
                    valkey_client.queue_federation_activity(activity, blog.id, blog.priv_key, blog_url, f"{actor}/inbox")
                else:
                    send_activity(activity, blog.priv_key, blog_url, f"{actor}/inbox")
        
    return redirect(f"/dashboard/edit/{blog.name}")

@dashboard_bp.route("/dashboard/preview", methods=['POST'])
def preview():
    if g.user is None:
        return redirect("/login")

    u = g.db.query(User).filter_by(id=g.user).first()
    data = {
        'title': request.form.get('title'),
        'content': sanitize_html(request.form.get('content')),
        'author': request.form.get('author'),
        'blog_title': request.form.get('blog_title'),
        'blog_name': request.form.get('blog_name'),
        'theme': request.form.get('theme'),
        'date': request.form.get('date'),
        'author_name': u.username
    }

    return render_template("preview.html", data=data)

@dashboard_bp.route("/dashboard/blog_preview", methods=['POST'])
def blog_preview():
    if g.user is None:
        return redirect("/login")

    u = g.db.query(User).filter_by(id=g.user).first()
    blog_name = request.referrer.split("/")[-1]
    blog = g.db.query(Blog).filter_by(name=blog_name).first()
    if not blog:
        abort(404)

    homepage = g.db.query(Page).filter(Page.blog == blog.id, Page.url == "").first()
    data = {
        'title': request.form.get('title'),
        'css': request.form.get('css'),
        'icon': request.form.get('icon'),
        'content': homepage.content_html,
        'theme': request.form.get('theme')
    }


    return render_template("blog_preview.html", data=data)

@dashboard_bp.route("/dashboard/edit/<blog>/<post>", methods=['GET', 'POST'])
def edit_post(blog, post):
    if g.user is None:
        return redirect("/login")

    blog_obj = g.db.query(Blog).filter_by(name=blog).first()
    if blog_obj is None or blog_obj.owner != g.user:
        abort(403)

    e_post = g.db.query(Post).filter_by(link=post).first()
    if request.method == "GET":
        return render_template("new_post.html", blog=blog_obj, post=e_post)

    p = g.db.query(Post).filter_by(link=post, blog=blog_obj.id).first()
    if not p:
        abort(404)

    title = request.form.get("title")
    if len(title) > 120:
        return render_template("new_post.html", blog=blog_obj, error="title-too-long")
    link = gen_link(title)
    if link == "rss":
        link = "p_rss"
    dupes_posts = g.db.query(Post).filter(Post.link.startswith(link), Post.blog == blog_obj.id).count()
    dupes_pages = g.db.query(Page).filter(Page.url == link, Page.blog == blog_obj.id).count()
    dupes = dupes_posts + dupes_pages
    if dupes > 0 and link != post:
        link += f"-{dupes + 1}"

    p.title = title
    now = datetime.now(timezone.utc).replace(microsecond=0)
    p.content_raw = request.form.get("content_raw")
    p.content_html = sanitize_html(request.form.get("content"))
    p.author = request.form.get("author")
    p.feed = request.form.get("feed")
    p.link = link
    if request.form.get("publish") == "1":
        p.date = now
    else:
        p.updated = now
    p.isdraft = request.form.get("draft", "0")
    g.db.commit()
    
    if blog_obj.access == "domain":
        blog_url = f"https://{blog_obj.name}.{g.main_domain}"
    else:
        blog_url = f"https://{g.main_domain}/b/{blog_obj.name}"

    followers = []
    if blog_obj.followers not in (None, "null", "NULL"):
        followers = json.loads(blog_obj.followers)

    if followers:
        activity_object = create_activity_object(p, blog_obj.name, blog_url, full_content=False)
        
        for actor in followers:
            now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            update_activity = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{blog_url}/{p.link}#update",
                "type": "Update",
                "actor": blog_url,
                "published": now_iso,
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": [f"https://{g.main_domain}/followers/{blog_obj.name}"],
                "object": activity_object
            }
            if valkey_client.is_enabled():
                valkey_client.queue_federation_activity(update_activity, blog_obj.id, blog_obj.priv_key, blog_url, f"{actor}/inbox")
            else:
                send_activity(update_activity, blog_obj.priv_key, blog_url, f"{actor}/inbox")

    return redirect(f"/dashboard/edit/{blog}")

@dashboard_bp.route("/dashboard/edit/<blog>/<post>/delete")
def delete_post(blog, post):
    if g.user is None:
        return redirect("/login")

    blog_obj = g.db.query(Blog).filter_by(name=blog).first()
    if blog_obj is None or blog_obj.owner != g.user:
        abort(403)

    p = g.db.query(Post).filter_by(link=post, blog=blog_obj.id).first()
    if p:
        if blog_obj.access == "domain":
            blog_url = f"https://{blog_obj.name}.{g.main_domain}"
        else:
            blog_url = f"https://{g.main_domain}/b/{blog_obj.name}"

        followers = []
        if blog_obj.followers not in (None, "null", "NULL"):
            followers = json.loads(blog_obj.followers)

        if followers:
            activity_object = create_activity_object(p, blog_obj.name, blog_url, full_content=False)
            
            for actor in followers:
                now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                delete_activity = {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "id": f"{blog_url}/{p.link}#delete",
                    "type": "Delete",
                    "actor": blog_url,
                    "published": now_iso,
                    "to": ["https://www.w3.org/ns/activitystreams#Public"],
                    "cc": [f"https://{g.main_domain}/followers/{blog_obj.name}"],
                    "object": activity_object
                }
                if valkey_client.is_enabled():
                    valkey_client.queue_federation_activity(delete_activity, blog_obj.id, blog_obj.priv_key, blog_url, f"{actor}/inbox")
                else:
                    send_activity(
                        delete_activity,
                        blog_obj.priv_key,
                        blog_url,
                        f"{actor}/inbox"
                    )
        
        g.db.delete(p)
        g.db.commit()

    return redirect(f"/dashboard/edit/{blog_obj.name}")



@dashboard_bp.route("/dashboard/changepw", methods=['GET', 'POST'])
def changepw():
    if g.user is None:
        return redirect("/login")

    if request.method == "GET":
       return render_template("changepw.html")

    old_pw = request.form.get("current_pass")
    new_pass = request.form.get("new_pass")
    new_pass2 = request.form.get("new_pass2")
    user = g.db.query(User).filter_by(id=g.user).first()
    if user and bcrypt.checkpw(old_pw.encode('utf-8'), user.password_hash.encode('utf-8')):
        if new_pass != new_pass2:
            return render_template("changepw.html", error='passwords_dont_match')
        hashed = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
        user.password_hash = hashed
        return redirect("/dashboard")

    else:
        return render_template("changepw.html", error='invalid_password')


@dashboard_bp.route("/dashboard/import", methods=['GET', 'POST'])
def migrate():
    if g.user is None:
        return redirect("/login")

    blogs = g.db.query(Blog).filter_by(owner=g.user).all()
    if request.method == "GET":
       return render_template("import.html", blogs=blogs)

    data = request.get_json()
    posts = data.get("posts")
    blog_d = data.get("blog")

    blog = g.db.query(Blog).filter_by(name=blog_d).first()
    if blog.owner != g.user:
        abort(403)

    for post in posts:
        title = post['title']
        content = post['content']
        date = datetime.strptime(post['date'], "%a, %d %b %Y %H:%M:%S %Z")

        if is_html(content):
            soup = BeautifulSoup(content, "html.parser")
            text_content = soup.get_text()
            html_content = content
        else:
            html_content = markdown.markdown(content)
            text_content = content
        new_post = Post(blog=blog.id, content_raw=text_content, content_html=html_content, author='0', feed='0', date=date, title=title, link=gen_link(title))
        g.db.add(new_post)
        g.db.commit()

    return "ok", 200

@dashboard_bp.route("/dashboard/stats/<blog>")
def stats(blog):
    if g.user is None:
        return redirect("/login")

    blog = g.db.query(Blog).filter_by(name=blog).first()
    if blog.owner != g.user:
        abort(403)

    posts = g.db.query(Post).filter_by(blog=blog.id).all()

    return render_template("stats.html", blog=blog, posts=posts)

@dashboard_bp.route("/dashboard/get_stats/<blog>/<post>/<limit>")
def get_stats(blog, post, limit):
    if g.user is None:
        abort(403)

    b = g.db.query(Blog).filter_by(id=blog).first()
    if g.user != b.owner:
        abort(403)

    if int(limit) not in (24, 168, 720, 2160):
        abort(400)
    time_threshold = datetime.now() - timedelta(hours=int(limit))
    views_obj = {}
    views_obj["views"] = []
    start_from = g.db.query(View).filter(View.blog == blog, View.post == post, View.date < time_threshold).count()
    views_obj["start_from"] = start_from
    views = g.db.query(View).filter(View.blog == blog, View.post == post, View.date >= time_threshold).all()
    for v in views:
        os = "Unknown"
        browser = "Unknown"
        if v.agent not in (None, "null", "NULL"):
            ua = parse(v.agent)
            os = ua.os.family
            browser = ua.browser.family
        views_obj["views"].append([v.date, os, browser])

    return views_obj

@dashboard_bp.route("/dashboard/page/<blog>", methods=['GET', 'POST'])
def new_page(blog):
    if g.user is None:
        abort(403)
    blog = g.db.query(Blog).filter_by(name=blog).first()

    if not blog:
        abort(404)

    if blog.owner != g.user:
        abort(403)

    if request.method == "GET":
        return render_template("new_page.html", blog=blog)

    name = request.form.get("name")
    url = request.form.get("url")
    content_raw = request.form.get("content_raw")
    content_html = request.form.get("content")
    show = request.form.get("show")
    if len(name) > 120:
        return render_template("new_page.html", blog=blog, error="name-too-long")
    if not re.match(r"^\/[a-zA-Z0-9\-\_]+$", url):
        return render_template("new_page.html", blog=blog, error="invalid-url")

    url = url[1:]
    if url == "rss":
        url = "p_rss"
    dupes_posts = g.db.query(Post).filter(Post.link.startswith(url), Post.blog == blog.id).count()
    dupes_pages = g.db.query(Page).filter(Page.url == url, Page.blog == blog.id).count()
    dupes = dupes_posts + dupes_pages
    if dupes > 0:
        url = f"{url}-{dupes + 1}"

    new_page = Page(blog=blog.id, name=name, url=url, content_raw=content_raw, content_html=sanitize_html(content_html), show=show)

    g.db.add(new_page)
    g.db.commit()
    return redirect(f"/dashboard/edit/{blog.name}")

@dashboard_bp.route("/dashboard/page/<page>/edit", methods=['GET', 'POST'])
def edit_page(page):
    if g.user is None:
        abort(403)

    page = g.db.query(Page).filter_by(id=page).first()
    if not page:
        abort(404)
    blog = g.db.query(Blog).filter_by(id=page.blog).first()

    if not blog:
        abort(404)

    if blog.owner != g.user:
        abort(403)
    home = False
    if page.url == "":
        home = True

    if request.method == 'GET':
        return render_template("new_page.html", blog=blog, page=page, home=home)

    name = request.form.get("name")
    content_raw = request.form.get("content_raw")
    content_html = request.form.get("content")
    show = request.form.get("show")
    url = request.form.get("url")
    if len(name) > 120:
        return render_template("new_page.html", blog=blog, page=page, home=home, error="name-too-long")
    if home == False:
        if not re.match(r"^\/[a-zA-Z0-9\-\_]+$", url):
            return render_template("new_page.html", blog=blog, error="invalid-url")

        url = url[1:]
        if url == "rss":
            url = "p_rss"
        dupes_posts = g.db.query(Post).filter(Post.link.startswith(url), Post.blog == blog.id).count()
        dupes_pages = g.db.query(Page).filter(Page.url == url, Page.blog == blog.id).count()
        dupes = dupes_posts + dupes_pages
        if dupes > 0 and url != page.url:
            url = f"{url}-{dupes + 1}"

    page.name = name
    page.content_raw = content_raw
    page.content_html = sanitize_html(content_html)
    page.show = show
    if home == False:
        page.url = url

    g.db.commit()
    return redirect(f"/dashboard/edit/{blog.name}")

@dashboard_bp.route("/dashboard/page_preview", methods=['POST'])
def page_preview():
    if g.user is None:
        return redirect("/")

    data = {
        'name': request.form.get('name'),
        'content': sanitize_html(request.form.get('content')),
        'blog_title': request.form.get('blog_title'),
        'blog_name': request.form.get('blog_name'),
        'theme': request.form.get('theme')
    }

    return render_template("page_preview.html", data=data)


@dashboard_bp.route("/dashboard/page/<page>/delete")
def page_delete(page):
    if g.user is None:
        return redirect("/")

    page = g.db.query(Page).filter_by(id=page).first()
    blog = g.db.query(Blog).filter_by(id=page.blog).first()

    if blog.owner != g.user:
        return abort(403)

    if page.url == "":
        return redirect("/dashboard")

    g.db.delete(page)
    g.db.commit()

    return redirect(f"/dashboard/edit/{blog.name}")

@dashboard_bp.route("/dashboard/export/<blog>")
def export_posts(blog):
    if g.user is None:
        return redirect("/login")

    blog_obj = g.db.query(Blog).filter_by(name=blog).first()
    if blog_obj is None or blog_obj.owner != g.user:
        return redirect("/dashboard")

    posts = g.db.query(Post).filter_by(blog=blog_obj.id).all()
    
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Title', 'Content Raw', 'Content HTML', 'Author', 'Link', 'Date', 'Updated', 'Feed', 'Is Draft'])
    
    for post in posts:
        writer.writerow([
            post.title,
            post.content_raw,
            post.content_html,
            post.author,
            post.link,
            post.date.isoformat() if post.date else '',
            post.updated.isoformat() if post.updated else '',
            post.feed,
            post.isdraft
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={blog}_posts.csv'
        }
    )
