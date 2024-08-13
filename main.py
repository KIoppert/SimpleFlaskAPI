from app import app

if __name__ == "__main__":
    app.run(debug=True)

# todo: DONE: 1) Finish the page with stats about the users. The page should be available at /users?id=x. \
#       DONE: 2) Fix button for delete and change info about user on /users?id=x. \
#       3) Add a page with a leaderboard of users. The page should be available at /users/leaderboard. \
#       DONE: 4) Add a page with a list of posts of a user. The page should be available at /users/<int:user_id>/posts.
