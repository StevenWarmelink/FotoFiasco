from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np
import textwrap
import json
import sys
import os

def create_cards_and_metadata_df():
    fnt = ImageFont.truetype("Pillow/Tests/fonts/DejaVuSans.ttf", 20)
    
    template_folder  = 'template_cards'
    dest_folder      = 'finished_cards'
    real_pics_folder = 'real_people'
    fake_pics_folder = 'fake_people'
    
    card_num = 1
    template_box = (99, 184, 647, 736)
    np.random.seed(1337)
    
    df = pd.DataFrame(columns = ['license', 'license_url', 'author', 'photo_url', 'original_url', 'file_path', 'card_number'])
    metadata_cols = ['license', 'license_url', 'author', 'photo_url']
    
    with open('ffhq-dataset-v2.json') as f:
        d = json.load(f)
        for difficulty in ['easy', 'hard']:
            real_cards = os.listdir(os.path.join(real_pics_folder, difficulty))
            real_cards.sort()
            fake_cards = os.listdir(os.path.join(fake_pics_folder, difficulty))
            fake_cards.sort()
            
            # combine folders
            all_cards = real_cards + fake_cards
            # only keep .jpg and .png
            all_cards = np.array([el for el in all_cards if el.endswith('jpg') or el.endswith('.png')])
            
            # reorder to random order (change seed for different results)
            permutation = list(np.random.permutation(52))
            all_cards = all_cards[permutation]
            with Image.open(os.path.join(template_folder, f"front_template_recolor_{difficulty}.png")) as template_front:                
                for card in all_cards:
                    if card.endswith('.jpg'):
                        origin = 'fake'
                    elif card.endswith('png'):
                        origin = 'real'
                    
                    picture_path = os.path.join(f'{origin}_people', difficulty, card)
                    with Image.open(picture_path) as portrait_im:
                        if difficulty == 'hard':
                            # crop out the bottom so credit doesnt give it away
                            portrait_im = portrait_im.crop((0, 0, 1000, 1000))
                        
                        portrait_im = portrait_im.resize((548, 552))
        
                        writeimg = template_front.copy()
                        writeimg.paste(portrait_im, template_box)
            
                        I1 = ImageDraw.Draw(writeimg)
                        I1.text((600, 1000), f"#{int(card_num):03}", font = fnt, fill=(40, 40, 40))
                        writeimg.save(os.path.join(dest_folder, f"{card_num:03}_front.png"))
                        
                        with Image.open(os.path.join(template_folder, f'back_recolor_{origin}_{difficulty}.png')) as back_img:
                            back_img.save(os.path.join(dest_folder, f"{card_num:03}_back.png"))
        
                        if origin == 'real':
                            el = str(int(card.split('.')[0]))
                            df_row = []
                            for metadata_col in metadata_cols:
                                df_row.append(d[el]['metadata'][metadata_col])
                            df_row.append(d[el]['image']['file_url'])
                            df_row.append(el)
                            df_row.append(card_num)
                            df.loc[len(df)] = df_row
                    card_num += 1
    
    df.to_csv(os.path.join(real_pics_folder, 'photo_metadata.csv'))
    return df

def create_manual_text(df):
    suffix_map = dict()
    suffix_map['Attribution License']               = '*'
    suffix_map['Attribution-NonCommercial License'] = '**'
    suffix_map['Public Domain Mark']                = '***'
    suffix_map['Public Domain Dedication (CC0)']    = '****'
    open("credits_for_manual.txt", "w").close() # clear file if it exists
    with open('credits_for_manual.txt', 'a') as the_file:
        for idx in range(len(df)):
            num       = df.loc[idx]["card_number"]
            author    = df.loc[idx]['author']
            author    = textwrap.fill(author, 30)           
            license   = df.loc[idx]['license']
            print_str = f"{num:03}: {author} {suffix_map[license]}\n"
            the_file.write(print_str)

if __name__ == '__main__':
    df = create_cards_and_metadata_df()
    create_manual_text(df)
