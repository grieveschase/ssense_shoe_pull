import requests, bs4, os, shelve
import requests.packages.urllib3
import urllib.request, json
from ebaysdk.trading import Connection
import sqlite3

#Edit1

class shoe:

    def __init__(self, json_data, us_sizes, shoe_url):
        self.BRAND = json_data["product"]["brand"]["name"].replace("&",'and')
        self.MODEL = json_data["product"]["name"].replace("&",'and')
        self.DESCRIPTION = json_data["product"]["description"].replace("&",'and')
        price = float(json_data["product"]["price"]['regular'])
        self.PRICE_ORIGINAL = price
        if price > 2000:
            new_price = round(price * 1.55)
        if price < 2000:
            new_price = round(price * 1.75)
        self.PRICE = new_price
        self.SIZES = us_sizes
        self.TOTAL_PRICE = len(us_sizes) * new_price
        #pic formatting
        pic_list = json_data["product"]["images"]
        pic_str = "https://img.ssensemedia.com/image/upload/b_white,c_lpad,g_center,h_960,w_960/c_scale,h_680/f_auto,dpr_1.0"
        self.PICTURES = [pic_str + pic.split("__IMAGE_PARAMS__")[-1] for pic in pic_list]
        self.URL = shoe_url
        self.SKU = json_data["product"]["sku"]

def shoe_url_to_info(shoe_url, price_threshold):
    res = requests.get(shoe_url + ".json")
    if res.status_code == 200:
        json_data = res.json()
        price = float(json_data["product"]["price"]['regular'])
        us_sizes = []
        sellable_size_bool = False
        for size_info in json_data["product"]["sizes"]:
            if size_info["inStock"]:
                size = float(size_info['name'])
                if size_info['nameSystemCode'] == 'IT':
                    size = size - 33.0
                if size_info['nameSystemCode'] == 'UK':
                    size = size + 1
                if (size >= 6.0) and (size <= 16.0):
                    us_sizes.append(size)
                    sellable_size_bool = True
        if sellable_size_bool and (price > price_threshold):
            shoe_info_class = shoe(json_data, us_sizes, shoe_url)
        else:
            shoe_info_class = None
    else:
        shoe_info_class = None
    return shoe_info_class

def display_info(shoe_info_class):
    print("BRAND: ", shoe_info_class.BRAND)
    print("MODEL: ", shoe_info_class.MODEL)
    print("DESCRIPTION: ",shoe_info_class.DESCRIPTION)
    print("PRICE: ",shoe_info_class.PRICE)
    print("PRICE_ORIGINAL: ",shoe_info_class.PRICE_ORIGINAL)
    print("TOTAL_PRICE: ",shoe_info_class.TOTAL_PRICE)
    print("SIZES: ",shoe_info_class.SIZES)
    print("PICTURES: ",shoe_info_class.PICTURES)
    print("URL: ",shoe_info_class.URL)
    print("SKU: ",shoe_info_class.SKU)

def html_description(shoe_info_class):
    html_string = "<![CDATA[<font face='Arial' size='6'><div style='text-align: center;'><b>Please be Certain of Sizing As We Are <font color='#FF0000'><u>NOT</u></font> Able to Take Returns.</b></div></font><div style='text-align: center;'><img src='PICTURE_URL'></div><div><font face='Arial' size='5'><b>BRAND_MODEL</b></font></div><div>  <p></p></div><div><font  face='Arial' size='4'><b>DESCRIPTION</b></font></div><div><p></p></div><div>  <font face='Arial' size='4'><b>Condition: Brand New</b></font></div><div><p></p></div><div>  <font face='Arial' size='4' color='#002cfd'> <b>100% authentic, We DO NOT sell Fakes/Variants/B-Grades</b></font></div><div> <p></p></div><div><font face='Arial' size='4'><b>Payment is due Immediately after auction ends. No Returns.  </b></font></div><div>    <p></p></div><div>  <font face='Arial' size='4'><b>Seller reserves the right to cancel bids or end the auction early for any reason. </b></font></div><div> <p></p></div><div> <font face='Arial' size='4' color='#ff0010'><b>International buyers please be aware that you are paying extra for postage to your location.  </b></font></div><div>    <p></p></div><div>  <font face='Arial' size='4'><b>Ships Double Boxed for maximum protection. </b></font></div><div><p></p></div><div>  <font face='Arial' size='4'><b>Message us with any questions not answered in this listing. </b></font></div>]]>"
    html_string = html_string.replace("PICTURE_URL",shoe_info_class.PICTURES[0])
    html_string = html_string.replace("BRAND_MODEL", str( shoe_info_class.BRAND + " " + shoe_info_class.MODEL))
    html_string = html_string.replace("DESCRIPTION", shoe_info_class.DESCRIPTION)
    return html_string

def AddFixedPriceItemShoe(shoe_info_class, post_debug = True, ebay_debug = True):
    Variation_list = []
    for size in shoe_info_class.SIZES:
        Variation_list.append({"Quantity":"1","StartPrice":str(shoe_info_class.PRICE),"VariationSpecifics": {"NameValueList": {"Name":"US Shoe Size (Men's)","Value":str(size)}}})

    api = Connection(config_file="ebay.yaml", debug=True)
    request = {
        "Item": {
            "BuyerRequirementDetails": {
                "ShipToRegistrationCountry": True
            },

            "Title": str(shoe_info_class.BRAND + str(" ") + shoe_info_class.MODEL),
            "Country": "US",
            "Location": "USA",
            "Site": "US",
            "ConditionID": "1000",
            "PaymentMethods": "PayPal",
            "PictureDetails": {"PictureURL":shoe_info_class.PICTURES},
            "PayPalEmailAddress": "c.grieves23@gmail.com",
            "PrimaryCategory": {"CategoryID": "24087"},
            "ProductListingDetails":{"BrandMPN":{"Brand":str(shoe_info_class.BRAND), "MPN":str(shoe_info_class.SKU)}},
            "Description": html_description(shoe_info_class),
            "ListingDuration": "Days_10",
            "StartPrice": str(shoe_info_class.PRICE),
            "Currency": "USD",
            "ReturnPolicy": {
                "ReturnsAcceptedOption": "ReturnsNotAccepted"
              },
            "ShippingDetails": {
                "ShippingServiceOptions": {
                    "FreeShipping": "True",
                    "ShippingService": "USPSMedia"
                },
                "ExcludeShipToLocation": "none"
            },
            "ItemSpecifics" :{"NameValueList":[{"Name":"Brand", "Value":str(shoe_info_class.BRAND)}, {"Name":"Style", "Value":"Fashion Shoe"}] },
            "Variations": {"VariationSpecificsSet": {
                               "NameValueList" : {
                                   "Name":"US Shoe Size (Men's)",
                                   "Value":[6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0,10.5,11.0,11.5,12.0,12.5,13.0,13.5,14.0,14.5,15.0,15.5,16.0],
                               }
                           },
                            "Variation":Variation_list
                                  },
            "DispatchTimeMax": '5',
        }
    }

    output = api.execute("AddFixedPriceItem", request)

    ItemID = output.reply.ItemID
    if post_debug:
        display_info(shoe_info_class)
    return ItemID


def total_amount_db():
    conn = sqlite3.connect("SHOE_DB.sqlite")
    cur = conn.cursor()

    sql_input = "SELECT PRICE FROM SHOES"
    cur.execute(sql_input)
    total = 0
    for row in cur:
        total += list(row)[0]
    print("Total in DB: ", total)
    cur.close()
    conn.close()
    return total
