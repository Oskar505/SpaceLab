import cv2
import numpy as np



def writeDataOnImage(data, imgName):
    imgPath = 'test/imgDataset/' + imgName
    img = cv2.imread(imgPath)

    # Text, který chceš napsat

    # Font a velikost písma
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 3
    font_thickness = 3
    font_color = (0, 0, 0)  # Černá barva
    background_color = (255, 255, 255)  # Bílá barva pro pozadí

    # Získání rozměrů textu
    text_size = cv2.getTextSize(data, font, font_size, font_thickness)[0]

    # Pozice pro text v pravém spodním rohu
    text_position = (img.shape[1] - text_size[0] - 10, img.shape[0] - 10)

    # Vytvoření bílého pozadí pro text
    background = np.ones((text_size[1] + 10, text_size[0] + 10, 3), dtype=np.uint8) * background_color

    # Vložení textu na bílé pozadí
    cv2.putText(background, data, (5, text_size[1] + 5), font, font_size, font_color, font_thickness)

    # Vložení bílého pozadí s textem na obrázek
    img[-(text_size[1] + 10):, -text_size[0] - 10:] = background


    # save to folder
    cv2.imwrite(f'test/imagesWithData/{imgName}', img)


    resizedImg = cv2.resize(img, (1014, 760))

    # Zobrazit obrázek s textem
    cv2.imshow('Image with Text', resizedImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


writeDataOnImage('test', 'andromeda_0001_53247677416_o.jpg')