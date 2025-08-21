"""
    This function differs from previous functions in that it enables multipage navigation, allowing you to freely return to the previous page, navigate to the next page, and return to the homepage. However, it does not have image functionality and is only suitable for quick apps without image features.
    If you need image functionality, please import the img_pages() function from easyapp_don.supermarket.imgbooks.Imgbook.
    It is actually a simplified version of the img_pages() function without image support, making it convenient for users who don't have image materials to run.
    The advantage is that you don't even need to write much code - just write a pages() function to create a simple 3-page scenario.
    Note that when writing the function, do not mistakenly write it as page() - that would be incorrect! page() is a function for creating a single page, which can create a multi-functional single page, not multiple pages like pages().
    The pages() function is the foundation of img_pages(). Let's talk about the parameters of Pagebook's pages().
    Special note: Sizes and positions are between 0 and 1, referring to the proportion of the parent container.
    :param page: This is a dictionary with numerous custom parameters. When writing this parameter, it's best to follow the format in easyapp_don.supermarket.pagebooks.__main__, where each page can automatically populate parameters. Many local parameters like tip also have custom sub-parameters such as txt, yie, ok, cal. You don't need to write all of them - just modify the parameters you want to change, achieving parameter freedom. We also emphasize fault tolerance. For example, in the text 2D list ts, the default position is the center (i.e., (0.5, 0.5)). If you don't want to change the position, just write the content, and we will automatically complete it for you.
    Take a look at the parameter format (not required; you only need to modify key parameters when filling in):
    {
    "Page1 name (not displayed)": {
    "tie": "This is the page title",
    "ts": [
    ["Hello, easyapp_don!", (0.5, 0.9)], # This is page content. The first part is text content, the second is position. If you don't want to write the position, you can omit it, and it will default to the center.
    ["Text1", (0.1, 0.65)],
    ["Text2", (0.5, 0.65)],
    ["Text3", (0.9, 0.65)],
    ["1/1", (0.5, 0.05)]
    ],
    "fs": [
    ["a[0]", GREY4, RED8, (0.05, 0.05), (0.1, 0.8)], # These are fill buttons for the page, like multiple-choice answer sheet buttons. They are a type of button that records its index when clicked and removes the index when clicked again.
    ["b[1]", GREY8, BLUE1, (0.05, 0.05), (0.5, 0.8)], # The first is the button text, the second is the initial color, the third is the color after clicking, the fourth is the size, and the fifth is the position. All have default values and can be abbreviated as [["example"]].
    ["c[2]", GREY8, GREEN8, (0.05, 0.05), (0.9, 0.8)]
    ],
    "es": [
    ["Enter1", (0.2, 0.05), (0.15, 0.5)], # These are input boxes for the page, which can input content and accurately display the input.
    ["Enter2", (0.2, 0.05), (0.5, 0.5)], # The first is the prompt content of the input box, the second is the size, and the third is the position.
    ["Enter3", (0.2, 0.05), (0.85, 0.5)] # You can abbreviate and omit the position, but it's not recommended for multiple input boxes as it may cause overlap in size and position.
    ],
    "bs": [
    ["Button0", RED1, (0.15, 0.05), (0.15, 0.3)], # These are button parameters. Clicking the button will immediately exit the set page and return a value.
    ["Button1", GREEN8, (0.15, 0.05), (0.5, 0.3)], # Its return value is its index. For example, clicking "Button1" will return 1.
    ["Button2", BLUE8, (0.15, 0.05), (0.85, 0.3)] # You can abbreviate, but it's not recommended as it may cause button overlap.
    ],
    "theme": LIGHT, # Page theme, there are LIGHT and DARK. You need to import from easyapp_don.tools.colors to get them.
    "color": WHITE12, # Page background color. You need to import from easyapp_don.tools.colors. The depth of the color is indicated by the number after it; the smaller the number, the darker the color.
    "tip": { # This is the input box that pops up when clicking to close the page. If you don't want it, set it to {}.
    "txt": "Close app?", # Text content of the pop-up
    "tie": "Tip", # Title of the pop-up
    "ok": ["Yes", GREY8], # OK button of the pop-up. The first is the text, the second is the color. You can also abbreviate to only the text.
    "cal": ["No", BLUE8] # Cancel button of the pop-up, same as the OK button. If you only want one button, set ok or cal to [].
    },
    "last": { # This is the previous navigation button of the page. Not available on the first page. txt is the button text, color is the button color.
    "txt": "<<Last",
    "color": ORANGE7,
    "size": (0.15, 0.05), # size is the button size
    "pos": (0.1, 0.1) # pos is the button position
    },
    "next": { # Similar to last, it navigates to the next page. Not available on the last page.
    "txt": "Next>>", # txt, color, size, pos are all button configurations
    "color": ORANGE7,
    "size": (0.15, 0.05),
    "pos": (0.9, 0.1)
    },
    "back": { # Similar to last, it functions to return to the homepage. Not available on the homepage.
    "txt": "<<<Back", # txt, color, size, pos are button configurations
    "color": ORANGE7,
    "size": (0.15, 0.05),
    "pos": (0.9, 0.95)
    }
    },
    "Page2 name (not displayed)": {...},
    ...
    "Page n name (not displayed)": {...}
    }
    :return: The return value is a dictionary. Format: {Page name (not title): [Clicked button, list of input texts, list of clicked fill buttons]}. For other questions, call 18903502392 to reach me!
    For complete examples, please refer to main.py
    """
__version__="0.2.2"
__author__="LvYanHua"
__all__=['Pagebook']