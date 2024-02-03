"""User model."""

from marshmallow import Schema, fields, post_load
from app import db


class User(db.Model):
    """
    User model.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    jobs = db.relationship("Job",
                           backref="owner", lazy=True)
    contact_email = db.Column(db.String(50), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)

    def __repr__(self) -> str:
        return f"User({self.id} - {self.username})"


class UserRequestSerialiser(Schema):
    """
    User request serializer.
    """
    username = fields.Str()
    password = fields.Str()

    @post_load
    def make_request(self, data, **kwargs):  # pylint: disable=W0613 # breaks if kwargs is removed
        """
        Deserialize.
        """
        return User(
            username=data["username"],
            password=data["password"],
            contact_email=data.get("contact_email", ""),
            contact_phone=data.get("contact_phone", ""),
        )


class UserResponseSerialiser(Schema):
    """
    User response serializer.
    """

    class Meta:
        """Meta."""
        fields = (
            "id",
            "username",
            "contact_email",
            "contact_phone"
        )


class UserRelatedSerialiser(Schema):
    """
    User related serializer.
    """

    class Meta:
        """Meta."""
        fields = (
            "id",
            "contact_email",
            "contact_phone"
        )
