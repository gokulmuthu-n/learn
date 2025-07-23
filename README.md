This is a space to learn stuff

* product-requirements.md is a copy of the file from [here](https://github.com/microsoft/github-copilot-vibe-coding-workshop/blob/main/product-requirements.md) It has requirements for a social media app that can be used to test automatic code generation, etc.
* Folder app was generated as a flask application of the social media app using GitHub Copilot
    - To start it, cd app; source venv/bin/activate; python app.py
    - These were the prompts used to generate the app
    - First iteration:
        * Using this product specification, generate a flask application in python.
        * Develop the backend using good REST API practices
        * Use sqlite for db with db file named model.db
        * Initialize db file before starting application if the db file is not already present
        * Use sqlalchemy to connect to db
        * Use the standard good practices of flask development
        * Handle errors gracefully
        * Use good variable names and url path names
        * Use jinja templates to develop a simple elegant colourful UI
        * Ensure that list items are linked to the items
        * Have elegant forms for each item type
        * Create requirements.txt and venv under app folder
        * Create the Flask application as a single python file called app.py
    - Subsequent iterations, one by one
        * Getting bad request when I click on like button
        * Add a initial login page. No password is needed. Remember the name of the logged in user for all forms where username is needed. The user need not give the username with every form.
        * The comment frontend should not allow to give username. It should use the logged in username
        * Give a link to the home page at the top of all pages
        * Allow editing of posts and comments only if the login name matches.
        * Dont show the edit and delete buttons in the ui itself if the login name does not match
        * Show the name of the current login at the top. Dont need to show username for every post and comment create/edit
        * Dont need to show username for like/dislike also
        * For all posts and comments, remember the timestamp of last update and display that too.
        * Display last updated times using the timezone of the browser



