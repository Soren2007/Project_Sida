from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from os.path import exists,getsize,join,isfile,basename
from os import chdir,remove,walk,listdir
from PIL import Image
from colorama import Fore
from time import sleep
from json import dump

images_path = input(f"{Fore.YELLOW} images file path >>> {Fore.GREEN}")

images_path.replace("\\", "/")

image_files = onlyfiles = [file for file in listdir(images_path) if isfile(join(images_path, file))]

def change_image_size(address):
    print(f"{Fore.GREEN}Changing image size{Fore.RESET} ===> {address}")
    image = Image.open(address)

    file_name = basename(image_files[0]).split(".")[0]
    file_format = basename(image_files[0]).split(".")[1]

    width, height = image.size
    new_size = (width//2, height//2)
    new_image = image.resize(new_size)

    original_size = getsize(address)
    new_image.save(address, optimize=True,quality=100)
    compressed_size = getsize(address)

    if compressed_size > 50000:
        return change_image_size(address)

    print(f"{Fore.GREEN}Changing image size {file_name}{Fore.RESET} ===> Succses")
    print(f"{Fore.GREEN}Original size{Fore.RESET} ===> {original_size}")
    print(f"{Fore.GREEN}Compressed size{Fore.RESET} ===> {compressed_size}")

    return {"address":address, "name":file_name}


browser = webdriver.Firefox()
browser.get('https://my.medu.ir/app/dashboards/teacher')


def find_students():
    obj_list = []
    students_element = browser.find_elements(By.CSS_SELECTOR, 'tbody[role="rowgroup"] > tr')
    for element in students_element:
        try:
            element.find_element(By.CSS_SELECTOR, 'img[src="/Sida/Content/img/thumb_default.jpg"]')
        except:
            continue
        uuid = element.get_attribute("data-uid")
        name = element.find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text
        family = element.find_element(By.CSS_SELECTOR, 'td:nth-child(5)').text
        obj_list.append({"uid":uuid,"name":name,"family":family})
    return obj_list


def add_data(data):
    with open('data.json', 'a+', encoding='utf-8') as json_file:
        dump(data, json_file, ensure_ascii=False, indent=4)

while True:
    flag = input(f"{Fore.GREEN}Do you want to continue? (y/n) {Fore.RESET}")
    if flag == "y":
        body = browser.find_element(By.CSS_SELECTOR, 'body')
        student_site_infos = find_students()
        student_info_list = []
        for info in student_site_infos:
            print(100*"-")
            print(f'{Fore.YELLOW}{info["uid"]} Start ....')
            image_flag = False
            for image in image_files:
                if f'{info["name"]} {info["family"]}' in image:
                    student_info = change_image_size(images_path + "/" + image)
                    image_flag = True
                    break
            
            if image_flag == False:
                print(f"{Fore.RED}   -------   {info["name"]}   ----  {info["family"]}")
                new_image_name = input(f"{Fore.RED}Image Not Found!!!\nEnter the name of the image or 0 for skeep: >>> {Fore.RESET}")
                if new_image_name == "0":
                    add_data(
                        {
                            "name" : info["name"],
                            "family":info["family"],
                            "uid":info["uid"],
                        }
                    )
                    continue
                student_info = change_image_size(images_path + "/" + new_image_name)

            sleep(2)
            student_element = body.find_element(By.CSS_SELECTOR, f'tr[data-uid="{info["uid"]}"]')
            edit_btn = student_element.find_element(By.CSS_SELECTOR, 'a[class="k-button k-button-icontext k-grid-edit"]')
            edit_btn.click()
            sleep(2)
            image_address = student_info["address"].replace("/","\\")
            image_input = browser.find_element(By.CSS_SELECTOR, f'input[id="imageUpload-avatar"]').send_keys(image_address)
            sleep(1)
            submit_btn = browser.find_element(By.CSS_SELECTOR, f'button[click="acceptStudent()"]')
            close_btn = browser.find_element(By.CSS_SELECTOR, f'i[ng-click="closePopup()"]')
            ActionChains(browser).move_to_element(close_btn).click().perform()
            print(f'{Fore.GREEN}{info["uid"]} Done .... {Fore.RESET}')
            sleep(2)
            print(100*"-")
    else:
        print(f"{Fore.RED}Exiting...{Fore.RESET}")
        browser.quit()
        exit(0)