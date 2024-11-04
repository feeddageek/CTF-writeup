def get_request_page(request):
    url_split = request.url.split("/")

    i = len(url_split) - 1

    page = ""

    while(i >= 0):
        try:
            if (url_split[i].index('.html') > 0):
                split_parameter = url_split[i].split("?")
                page = split_parameter[0].lower()
                break
        except ValueError:
            i -= 1
            continue
    
    return f"/{page}"