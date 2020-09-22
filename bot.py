import zulip

client = zulip.Client(config_file="zuliprc-user")

FILTER_GROUPS = [4, 7]  # Orga/Mentoring

class BotHandler(object):
    def usage(self):
        return "Zulip language bot POC"

    def handle_message(self, message, bot_handler):
        sid = message["sender_id"]
        split = message["content"].split()
        cmd = split[0].lower()
        resp = get_groups()
        if resp["result"] != "success":
            return bot_handler.send_reply(message, "gERROR")

        groups = resp["user_groups"]

        content = "-"
        if cmd in ["get", "list"]:
            content = "Groups: " + ", ".join([group["name"] for group in groups if group["id"] not in FILTER_GROUPS and sid in group["members"]])

        elif cmd in ["add"]:
            # TODO: Filter
            # TODO: Approx name
            names = "".join(split[1:]).lower().strip().split(",")
            for name in names:
                if group_exists(groups, name):
                    group = get_group_by_name(groups, name)
                    if not has_group(group, sid):
                        result = client.update_user_group_members({
                            "group_id": group["id"],
                            "add": [sid],
                        })
                        print(result)
                else:
                    result = client.create_user_group({
                        "name": name,
                        "description": "A skill group",
                        "members": [sid],
                    })
                    print(result)  # Creates an error
            content = "Groups added!"

        elif cmd in ["delete", "remove"]:
            names = "-".join(split[1:]).lower().strip().split(",")
            for name in names:
                if group_exists(groups, name): # TODO: group_exists with walrus :=
                    group = get_group_by_name(groups, name)
                    if has_group(group, sid):
                        result = client.update_user_group_members({
                            "group_id": group["id"],
                            "delete": [sid],
                        })
            content = "Groups deleted!"

        else:
            content = "Command does not exist!"
        bot_handler.send_reply(message, content)

handler_class = BotHandler

def get_groups():
    return client.get_user_groups()


def group_exists(groups, name):
    return name in get_group_names(groups)


def has_group(group, sid):
    return sid in group["members"]


def get_group_names(groups):
    return [group["name"] for group in groups]


def get_group_by_name(groups, name):
    # TODO: Approx name
    for group in groups:
        if group["name"] == name:
            return group


def get_group_name_by_id(groups, id):
    return ""
