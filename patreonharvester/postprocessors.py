from PIL import Image, UnidentifiedImageError

import os
import logging

logger = logging.getLogger("patreonharvester."+__name__)

class ImagePostProcessor():
    def __init__(self, in_dir:str , out_dir:str):
        self.in_dir = in_dir
        self.out_dir = out_dir
        self.images = []

    def get_all_images(self):
        for file in os.listdir(self.in_dir):
            self.images.append(file)

        logger.info(f"Got {len(self.images)} files")
        return 

    def get_cache(self):
        self.cache= set()
        for file in os.listdir(self.out_dir):
            self.cache.add(file)

        logger.info(f"Got {len(self.cache)} images")
        return


    def process(self, path_list):
        pass


class ImageResizer(ImagePostProcessor):

    def process(self):
        self.get_all_images()
        self.get_cache()
        self.resize_imgs()
        return

    def resize_imgs(self):
        proccessed_imgs = 0
        for img_file in self.images:
            if img_file in self.cache:
                continue

            input_path = self.in_dir + img_file
            if not os.path.isfile(input_path):
                logger.error(f'{input_path} not and image')
                continue
            try:
                img = Image.open(input_path)
                img.thumbnail([300,300])
                out_path = self.out_dir + img_file
                proccessed_imgs += 1
                logger.info(f'Saving {self.out_dir + img_file}')
                img.save(out_path)
            except ValueError as e:
                logger.error(e)
                logger.error(f'Error saving {out_path}')
            except UnidentifiedImageError as e:
                logger.error(e)
                logger.error(f'Error saving {out_path}')
        return
