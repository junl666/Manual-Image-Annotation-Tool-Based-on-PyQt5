import base64
import contextlib
import io
import json
import os.path as osp
import PIL.Image
import utils
import logging

logger = logging.getLogger("labelall")
PY2 = "2"
QT4 = "4"
PIL.Image.MAX_IMAGE_PIXELS = None


@contextlib.contextmanager
def open(name, mode):
    """打开json文件

    Args:
        name(str): json文件的绝对路径
        mode(str): 打开的形式

    """
    assert mode in ["r", "w"]
    if PY2:
        mode += "b"
        encoding = None
    else:
        encoding = "utf-8"
    yield io.open(name, mode, encoding=encoding)
    return


class LabelFile(object):
    """得到图片或json文件的label信息和图片的编码信息

    """
    suffix = ".json"

    def __init__(self, filename=None):
        """

        Args:
            filename(str): 图片对应的json文件的绝对路径

        """
        self.shapes = []
        self.imagePath = None
        self.imageData = None
        if filename is not None:
            self.load(filename)
        self.filename = filename

    @staticmethod
    def load_image_file(filename):
        """通过图片路径，返回其编码的信息

        Args:
            filename(str): 图片的绝对路径

        Returns:
            图片的编码后的信息

        """
        try:
            image_pil = PIL.Image.open(filename)
        except IOError:
            logger.error("Failed opening image file: {}".format(filename))
            return

        # apply orientation to image according to exif
        image_pil = utils.apply_exif_orientation(image_pil)

        with io.BytesIO() as f:
            ext = osp.splitext(filename)[1].lower()
            if PY2 and QT4:
                format = "PNG"
            elif ext in [".jpg", ".jpeg"]:
                format = "JPEG"
            else:
                format = "PNG"
            image_pil.save(f, format=format)
            f.seek(0)
            return f.read()

    def load(self, filename):
        """ 读取json文件，并获得相关信息

        Args:
            filename(str): json文件的绝对路径

        """
        keys = [
            "version",
            "imageData",
            "imagePath",
            "shapes",  # polygonal annotations
            "flags",  # image level flags
            "imageHeight",
            "imageWidth",
        ]
        shape_keys = [
            "label",
            "points",
            "group_id",
            "shape_type",
            "flags",
        ]

        with open(filename, "r") as f:
            data = json.load(f)
        version = data.get("version")
        if version is None:
            logger.warn(
                "Loading JSON file ({}) of unknown version".format(
                    filename
                )
            )
        elif version.split(".")[0] != "5.0.1".split(".")[0]:
            logger.warn(
                "This JSON file ({}) may be incompatible with "
                "current labelme. version in file: {}, "
                "current version: {}".format(
                    filename, version, "5.0.1"
                )
            )

        if data["imageData"] is not None:
            global imageData_again
            imageData_again = data["imageData"]
            imageData = base64.b64decode(data["imageData"])
            if PY2 and QT4:
                imageData = utils.img_data_to_png_data(imageData)
        else:
            # relative path from label file to relative path from cwd
            imagePath = osp.join(osp.dirname(filename), data["imagePath"])
            imageData = self.load_image_file(imagePath)
        flags = data.get("flags") or {}
        imagePath = data["imagePath"]
        shapes = [
            dict(
                label=s["label"],
                points=s["points"],
                shape_type=s.get("shape_type", "polygon"),
                flags=s.get("flags", {}),
                group_id=s.get("group_id"),
                other_data={
                    k: v for k, v in s.items() if k not in shape_keys
                },
            )
            for s in data["shapes"]
        ]

        otherData = {}
        for key, value in data.items():
            if key not in keys:
                otherData[key] = value

        # Only replace data after everything is loaded.
        self.flags = flags
        self.shapes = shapes
        self.imagePath = imagePath
        self.imageData = imageData
        self.filename = filename
        self.otherData = otherData

