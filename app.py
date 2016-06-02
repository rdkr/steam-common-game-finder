import os
from flask import Flask, request, render_template
from steamapi.steamapi import core, user, errors

core.APIConnection(api_key=os.environ['STEAM_WEB_API_KEY'])

application = Flask(__name__)


@app.route('/submit', methods=['GET'])
def submit():

    valid_steam_users = []
    restricted_steam_users = []
    invalid_steam_users = []

    # if no ids are proivided in GET request, return the index page
    if request.args.get('ids', '') == '':
        return render_template('index.html')

    # attempt to create SteamUser objects for each provided id. if succesful,
    # check the games list is not private

    for submitted_id in request.args.get('ids', '').replace(' ', '').split(','):
        if len(submitted_id) is 0:
            continue
        try:
            steam_user = user.SteamUser(userurl=submitted_id)
            try:
                steam_user.games
                valid_steam_users.append(steam_user)
            except errors.AccessException:
                restricted_steam_users.append(steam_user)
        except errors.UserNotFoundError:
            try:
                steam_user = user.SteamUser(userid=int(submitted_id))
                try:
                    steam_user.games
                    valid_steam_users.append(steam_user)
                except errors.AccessException:
                    restricted_steam_users.append(steam_user)
            except (ValueError, errors.UserNotFoundError):
                invalid_steam_users.append(submitted_id)

    # if no valid ids, return index with list of invalid / restricted ids

    if not valid_steam_users:
        return render_template('index.html',
                               requested_ids=request.args.get(
                                   'ids', '').replace(' ', ''),
                               restricted_steam_users=restricted_steam_users,
                               invalid_steam_users=invalid_steam_users
                               )

    # create a list of the set of game ids each valid user owns

    valid_steam_users_game_ids_set_list = []

    for steam_user in valid_steam_users:
        valid_steam_users_game_ids_set_list.append(
            set(game._id for game in steam_user.games))

    # find the intersection of owned games (ie common games)

    common_games_game_id_set = set.intersection(
        *valid_steam_users_game_ids_set_list)

    # create a dictionary with user as key and a dictionary of their play time
    # in each common game as value

    common_games_playtimes_dict = {}

    for steam_user in valid_steam_users:
        steam_user_common_games = {}
        for game in steam_user.games:
            if game._id in common_games_game_id_set:
                steam_user_common_games[game._id] = game.playtime_forever
        common_games_playtimes_dict[steam_user._id] = steam_user_common_games

    # create a dictionary containing the average play time across players for
    # each game

    common_games_average_playtime = {}

    for game_id in common_games_game_id_set:
        common_games_average_playtime[game_id] = 0
        for steam_user in common_games_playtimes_dict:
            common_games_average_playtime[
                game_id] += common_games_playtimes_dict[steam_user][game_id] / len(valid_steam_users)

    # sort a list of common games according to the average play time of each
    # game

    common_games = []

    for game_id in sorted(common_games_average_playtime, key=common_games_average_playtime.get, reverse=True):
        for game in valid_steam_users[0].games:
            if game_id == game._id:
                common_games.append(game)
                break

    # return the results

    return render_template('index.html',
                           requested_ids=request.args.get(
                               'ids', '').replace(' ', ''),
                           games=[game.name for game in common_games],
                           restricted_steam_users=restricted_steam_users,
                           invalid_steam_users=invalid_steam_users,
                           valid_steam_users=valid_steam_users
                           )


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    application.run(debug=True, host="0.0.0.0", port=8232)
