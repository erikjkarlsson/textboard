from flask import Flask, render_template, request
from html import escape
import os
import base64
import random

app = Flask(__name__)

# Get amount of replys
def get_current_id():
    id_file  = open("reply/information/current_id", "r")
    id       = id_file.read()
    id_file.close()

    return int(id)

# Rewrite the amount of replys
def write_new_id(new_id):
    id_file = open("reply/information/current_id", "w")
    id_file.write(str(new_id))
    id_file.close()

    return int(new_id)

def remove_all_posts():
    try:
        write_new_id(0) # Change amount of posts
            
        return True
    except:
        return False


def create_new_reply(
        name = "Anonymous",
        subject = "",
        message = None,
        special_action = None
    ):

    if ( not ((message == None) or (message == "") or (message == "\n"))):
        # update amount of replys
        id = get_current_id()
        write_new_id(id + 1)


        try:
            f = open("reply/messages/%s"%id, "w")
            f.write("%s\n%s\n%s\n%s\n%s"%(
                base64.b64encode(bytes( escape(name),           'utf-8')).decode('utf-8'),
                base64.b64encode(bytes( escape(subject),        'utf-8')).decode('utf-8'),
                base64.b64encode(bytes( escape(str(id)),        'utf-8')).decode('utf-8'),
                base64.b64encode(bytes( escape(message),        'utf-8')).decode('utf-8'),
                base64.b64encode(bytes( escape(special_action), 'utf-8')).decode('utf-8'))
                    )
            f.close()
            return True
        except:
            return False

def read_replys():
    reply_list = []
    for reply in range(0, get_current_id()):
        # Format: name \n subject \n id \n message \n special action
        f = open("reply/messages/%s"%(str(reply)), "r")
        reply_list.append(f.read().split("\n"))
        f.close()

    return reply_list


def format_replys(replys):
    formated_replys = []

    for reply in replys:

        name           = base64.b64decode(reply[0]).decode('utf-8')
        subject        = base64.b64decode(reply[1]).decode('utf-8')
        id             = base64.b64decode(reply[2]).decode('utf-8')
        message        = base64.b64decode(reply[3]).decode('utf-8')
        special_action = base64.b64decode(reply[4]).decode('utf-8')

        
        bigtext     = False
        greentext   = False
        new_message = ""

        # >
        message = message.replace("&gt;", "\x99")
        message = message.replace("&#35;", "\x98")

        last_char = '\n'
        
        for char in message:
            try:
                if (not greentext) and (char == "\x99") and (last_char == "\n"):
                    # Greentext first char
                    
                    new_message += "<span class=\"greentext\">&gt;"
                    greentext    = True

                elif (char == "\x99"):
                    # Not greentext but arrow
                    new_message += "&gt;"

                elif (char == "\n"):   
                    # Add newline
                    if (greentext):
                        new_message += "</span>"
                        greentext    = False
                        
                    last_char    = "\n"
                    new_message += "<br>"
                else:
                    new_message += char
                    last_char    = char
            except:
                None

        # Add newline
        if (greentext):
            new_message += "</div>"
            greentext = False
        # Add big text
        if (bigtext):
            new_message += "</h4>"
            bigtext = False

        new_message.replace("\x99", "")
        new_message.replace("\x98", "")
        print(new_message, "\n\n")
        formated_replys.append(
            """
            <div class="user_reply">
                <table id="user_reply_header">
                    <tr>
                        <td id="h_name">%s</td>
                        <td id="h_sub"><span id="name_s"></span><b>%s</b></td>
                        <td id="h_id"><span id="id_s">No.</span>%s</td>
                    </tr>
                    
                    <tr>
                        <td><p id="user_reply_text"> %s</p></td>
                    </tr>
                </table>
            </div>
            """%(

                str(name),
                str(subject),
                str(id),
                str(new_message)))

    return formated_replys

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        # Get reply information
        message        = request.form["reply_message"]
        name           = request.form["reply_name"]
        subject        = request.form["reply_subject"]
        special_action = request.form["reply_sa"]
        
        if (special_action == "R-ALL"):
            remove_all_posts()
        
        create_new_reply(name, subject, message, special_action)

    replys = format_replys(read_replys())

    return render_template("message.html", replys=replys)

if __name__ == "__main__":
    app.run()

