def name_data():
    return {
        "names": ["Jannik"],
        "numbers": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "alphabet": [chr(x) for x in range(65, 65 + 26)]
    }


def static_stream():
    def item(
            content="Hello World",
            content_url="https://jbamberger.de/",
            order_date=1337,
            image_url="https://jbamberger.de/static/pig.jpg"):
        return {'content': content, 'content_url': content_url, 'order_date': order_date, 'image_url': image_url}

    return [
        item("Good morning"),
        item(),
        item(),
        item(),
        item(),
        item(),
        item(),
        item(),
        item()
    ]
