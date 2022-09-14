from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from flask_migrate import Migrate


app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:root@localhost:5432/simpleblog"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

##Database Model
##One to many Relationship

post_tag = db.Table(
    "post_tag",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return f'< Tag "{self.name}">'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    # encoding the relaionship btw post & comment table
    # you use the backref parameter to add a back reference
    # that behaves like a column to the Comment model.
    comments = db.relationship("Comment", backref="post")
    tags = db.relationship("Tag", secondary=post_tag, backref="posts")
    # you use a backref parameter to add a back reference that behaves like a column to the Tag model.
    # This way, you can access the tag's posts via tag.posts and the tags of a post via post.tags.

    def __repr__(self):
        return f'<post "{self.title}">'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

    def __repr__(self):
        return f'<commet "{self.content[:20]}">'


@app.route("/")
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route("/<int:post_id>/", methods=("GET", "POST"))
def post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        comment = Comment(content=request.form["content"], post=post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("post", post_id=post.id))
    return render_template("post.html", post=post)


@app.route("/comments/")
def comments():
    comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template("comments.html", comments=comments)


@app.post("/comments/<int:comment_id>/delete")
def delete_comment(comment_id):
    ##get the id of the element to delete on the child model
    ##using url variable comment_id
    comment = Comment.query.get_or_404(comment_id)

    ##get the id of the parent model
    ## i.e referencing parent table with comment.post.id
    ## using post_id to redirect to post page
    post_id = comment.post.id
    db.session.delete(comment)
    return redirect(url_for("post", post_id=post_id))


## Displaying Tags and Their Posts
@app.route("/tags/<tag_name>/")
def tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    return render_template("tag.html", tag=tag)
