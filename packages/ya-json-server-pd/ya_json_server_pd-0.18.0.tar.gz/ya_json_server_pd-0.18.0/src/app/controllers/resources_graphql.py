def get_items_as_fields(items: dict) -> list[tuple[str, str]]:
    result = [(str(k), str(type(v)).split("'")[1]) for k, v in items]
    return result


def get_resources_data(cls_union):
    # get a class to create sample data
    cls = cls_union[0]
    # TODO: get real data using JsonContentModel
    result = [
        cls(
            id=1,
            company="Chang-Fisher",
            city="Tammyfort",
            country="OrangeCity",
            postcode=40256,
            pricetag=45593.82,
        ),
        cls(
            id=1,
            company="Chang-Fisher",
            city="Jacarta",
            country="BlueCity",
            postcode=40256,
            pricetag=45593.82,
        ),
    ]
    return result
