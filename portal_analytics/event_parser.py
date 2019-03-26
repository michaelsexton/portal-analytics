def create_event_db(rows):
    wrong_iter = 0
    for row in rows:
        if row[0] in ["New:LayerInteraction"]:
            create_layer_interaction_event(row)
        elif row[0] in ["Add:CSWRecord", "Add:KnownLayer"]:
            create_add_layer_event(row)
        elif row[0] in ["Add:search", "Advanced Search:","New:Search"]:
           create_search_event(row)
        elif row[0] in ["ClearMapHandlerClick","Custom WMS Query","PermanentLinkHandlerClick","PrintMapHandlerClick","ScannedMapsHandlerClick","New:Help Panel","New:CustomUI"]:
            create_custom_event(row)
        elif row[0] in ["FileDownloader","KLWFSDownloader","NVCL:TSG DOWNLOAD","New:Downloads"]:
            create_download_event(row)
        elif row[0] in ["Query","New:Query"]:
            create_query_event(row)
        else:
            print("Unknown event type: " + row[0])
            wrong_iter += 1
        if wrong_iter > 10:
            break

def create_layer_interaction_event(row):
    if row[1] == "About":
        return create_custom_event(row)
    elif row[1] == "Add":
        return create_add_layer_event(row)
    elif row[1] == "Remove":
        return create_remove_layer_event(row)




def create_add_layer_event(row):
    if row[0] == "New:LayerInteraction":
        parse_data_structure(row[2])
    else:
        print(row)
        raise Exception

def create_search_event(row):
    pass


def create_download_event(row):
    pass




def create_remove_layer_event(row):
    pass

def create_custom_event(row):
    pass


def create_query_event(row):
    pass


def parse_data_structure(param):
    pass