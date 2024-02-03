"""
Job model.
"""
from marshmallow import Schema, fields, post_load
from app import db
from app.models.user import UserRelatedSerialiser, User


class Tag(db.Model):
    """
    Tag model.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)


class TagSerializer(Schema):
    """
    Tag serializer.
    """

    class Meta:
        """
        Meta.
        """

        fields = (
            "id",
            "name",
        )


job_tag = db.Table(
    'job_tag',
    db.Column('job_id', db.Integer, db.ForeignKey('job.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Job(db.Model):
    """
    Model for Job.
    """
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    video_link = db.Column(db.String(300), nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    site_link = db.Column(db.String(300), nullable=True)
    location = db.Column(db.String(20), nullable=True)

    valid_until = db.Column(db.DateTime, nullable=True)

    tags = db.relationship('Tag', secondary=job_tag,
                           backref='jobs', lazy='dynamic')

    def __repr__(self) -> str:
        return f"Job({self.id})"


class JobResponseSerializer(Schema):
    """
    Job response serializer.
    """

    user = fields.Method("get_user_data")
    tags = fields.Method("get_tag_data")

    class Meta:
        """
        Meta.
        """

        fields = (
            "id",
            "title",
            "text",
            "user",
            "video_link",
            "site_link",
            "valid_until",
            "location",
            "tags"
        )

    def get_user_data(self, obj):
        """
        User data related to Job.
        """
        user_id = obj.user_id
        user = User.query.get(user_id)

        user_data = UserRelatedSerialiser().dump(user)

        return user_data

    def get_tag_data(self, obj):
        """
        Job related tags.
        """
        tags = obj.tags.all()
        tag_data = TagSerializer(many=True).dump(tags)
        return tag_data


class JobRequestSerializer(Schema):
    """
    Job request serializer.
    """
    text = fields.Str()
    title = fields.Str()
    user_id = fields.Int()

    video_link = fields.Str()
    image_url = fields.Str()
    site_link = fields.Str()

    @post_load
    def make_request(self, data, **kwargs):  # pylint: disable=W0613 # breaks if kwargs is removed
        """
        Deserialize.
        """
        return Job(
            **data
        )
