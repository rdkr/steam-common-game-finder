import os
from flask import Flask, request, render_template
from steamapi.steamapi import core, user, errors

core.APIConnection(api_key=os.environ['STEAM_WEB_API_KEY'])

app = Flask(__name__)


@app.route('/submit', methods=['GET'])
def submit():

    valid_steam_users = []
    restricted_steam_users = []
    invalid_steam_users = []

    # get submitted id and check they are valid

    if request.args.get('ids', '') == '':
        return render_template('index.html')

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

    # if no valid ids, return with list of invalid ids

    if not valid_steam_users:
        return render_template('index.html',
                               requested_ids=request.args.get(
                                   'ids', '').replace(' ', ''),
                               restricted_steam_users=restricted_steam_users,
                               invalid_steam_users=invalid_steam_users
                               )

    # create a list of the set of game ids each user owns

    valid_steam_users_game_ids_set_list = []

    for steam_user in valid_steam_users:
        valid_steam_users_game_ids_set_list.append(
            set(game._id for game in steam_user.games))

    # find the intersection of owned games (ie common games)

    common_games_game_id_set = set.intersection(
        *valid_steam_users_game_ids_set_list)

    # ####

    common_games_playtimes_dict = {}

    for steam_user in valid_steam_users:
        steam_user_common_games = {}
        for game in steam_user.games:
            if game._id in common_games_game_id_set:
                steam_user_common_games[game._id] = game.playtime_forever
        common_games_playtimes_dict[steam_user._id] = steam_user_common_games

    common_games_average_playtime = {}

    for game_id in common_games_game_id_set:
        common_games_average_playtime[game_id] = 0
        for steam_user in common_games_playtimes_dict:
            common_games_average_playtime[
                game_id] += common_games_playtimes_dict[steam_user][game_id] / len(valid_steam_users)

    common_games = []

    for game_id in sorted(common_games_average_playtime, key=common_games_average_playtime.get, reverse=True):
        for game in valid_steam_users[0].games:
            if game_id == game._id:
                common_games.append(game)
                break

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

app.run(debug=True, host="0.0.0.0", port=8000)
