"""Web Server Gateway Interface"""

##################
# FOR PRODUCTION
####################

from app import app

application = app

if __name__ == "__main__":
    # app.run(host='127.0.0.1:5000', debug=True, ssl_context='adhoc')
    app.run(debug=True)

# if __name__ == "__main__":
#     ####################
#     # FOR DEVELOPMENT
#     ####################
#     app.run(host='127.0.0.1', debug=True, ssl_context='adhoc')

# if __name__ == '__main__':
#     context = ('local.crt', 'local.key')#certificate and key files
#     app.run(debug=True, ssl_context=context)
