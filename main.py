"""
Main file for app.
"""
from flask import request
from app import app, db
from app.routes.user_routes import users_blueprint
from app.utils.func import decode_token, renew_tokens, has_logged_in
from app.models.job import Job, JobResponseSerializer, JobRequestSerializer, Tag


@app.after_request
def renew_expired_access_token(response):
    """
    Checking before request.
    """
    access_token = request.cookies.get("access_token", None)
    if access_token and not decode_token(access_token):
        refresh_token = request.cookies.get("refresh_token", None)

        if refresh_token:
            decoded_refresh = decode_token(refresh_token)

            if decoded_refresh:
                # renew tokens
                response = renew_tokens(response, decoded_refresh)

    return response


@app.route("/job", methods=["GET"])
def job():
    """
    Job router.
    """
    job_query = Job.query.all()
    return JobResponseSerializer().dump(obj=job_query, many=True),   200


@app.route("/job", methods=["POST"])
def add_job():
    """
    Job router.
    """
    token = has_logged_in(request)

    if not token:
        return {"message": "not authorized"}, 403

    data = request.json

    request_tags = data.pop("tags", [])
    request_tags = [t.lower() for t in request_tags]

    existing_tags = Tag.query.filter(Tag.name.in_(request_tags))
    new_tags = None

    if len(request_tags) != existing_tags.count():
        found_tag_names = [tag.name for tag in existing_tags]
        tags_to_create = [t for t in request_tags if t not in found_tag_names]
        new_tags = [Tag(name=n) for n in tags_to_create]

    new_job = JobRequestSerializer().load(data={
        "user_id": token["id"],
        **data
    })
    for t in existing_tags:
        new_job.tags.append(t)

    if new_tags:
        for t in new_tags:
            new_job.tags.append(t)

    db.session.add(new_job)
    db.session.commit()

    return JobResponseSerializer().dump(new_job), 201


app.register_blueprint(users_blueprint)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="localhost", port=3000, debug=True)
