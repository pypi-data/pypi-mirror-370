from marshmallow import Schema, fields
from ..bbox_coord_schema import BboxCoordAttrsSchema
from ..bbox_pixels_coord_schema import BboxPixelsCoordAttrsSchema
from ..keypoints_pixels_coord_schema import KeypointsPixelsCoordAttrsSchema
from ..category_schema import CategoryAttrsSchema
from ..image_schema import ImageAttrsSchema
from ..inferred_schema import InferredAttrsSchema
from ..chip_detection_schema import ChipDetectionAttrsSchema


class DetectionSchema(Schema):
    id = fields.String()
    bbox_coord = fields.Nested(BboxCoordAttrsSchema())
    bbox_pixels_coord = fields.Nested(BboxPixelsCoordAttrsSchema())
    bbox_pixels_coord_area = fields.Int()
    keypoints = fields.Nested(KeypointsPixelsCoordAttrsSchema())
    shadow_detection = fields.String(defualt="NA")
    category = fields.Nested(CategoryAttrsSchema())
    image = fields.Nested(ImageAttrsSchema())
    inferred = fields.Nested(InferredAttrsSchema())
    score = fields.Float()
    chip_detection = fields.Nested(ChipDetectionAttrsSchema())
