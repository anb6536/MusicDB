import psycopg2
import datetime
import time

"""
Music App to manipulate the Database
Authors: Aahish Balimane, Michael Berger, Asha Kadagala
"""

def connect():
    """
    Function to connect to our database with our DB Credentials
    """
    try:
        connection = psycopg2.connect(  user="p320_36",
                                        password="HohshiNeithae9phethi",
                                        host="reddwarf.cs.rit.edu",
                                        port="5432",
                                        database="p320_36")
        cursor = connection.cursor()
        return connection, cursor
    except(Exception, psycopg2.Error):
        print("Error connecting to the database")


def close(connection, cursor):
    """
    This function is used to close the connection with the database
    after the program is ended.
    """
    if(connection):
        cursor.close()
        connection.close()
        print("Connection Closed Successfully")

def help():
    """
    This function is used to display a help message with the valid 
    commands.
    """
    print("\nAvailable commands are:")
    print("\t'create collection': to create a collection for yourself (1 per user)")
    print("\t'search': to search for a song,artist or album")
    print("\t'collection add': to add a song, album, artist to your collection")
    print("\t'play': to play a song from the entire library")
    print("\t'add to database': add a song, album or artist to the overall database")
    print("\t'quit': to exit the application")
    

def login(username, password, cursor):
    """
    This function is used to log in the user into the application
    param username: The username of the user
    param password: The password for the user
    param cursor: the cursor used to send queries to the database
    """
    try:
        query = '''
                SELECT COUNT(user_id) FROM USERS 
                WHERE USERNAME=\'''' + username + '''\' AND PASSWORD=\'''' + password + '''\''''
        count = cursor.execute(query)
        if(count!=0):
            query = '''
                SELECT user_id FROM USERS 
                WHERE USERNAME=\'''' + username + '''\' AND PASSWORD=\'''' + password + '''\''''
            cursor.execute(query)
            user_id = cursor.fetchone()[0]
            return user_id
        else:
            print("Login Unsuccessful\n")
            print("Try Again!\n")
            return None
    except(Exception, psycopg2.Error):
        return None

def signup(username, password, cursor, connection):
    """
    This function is used for users who don't have an account and 
    would like to sign up for one
    param username: The username the user wants to use
    param password: The password the user want to register with
    param cursor: to send the queries to the database
    param connection: to commit changes to the database
    """
    query = '''
            INSERT INTO USERS (USERNAME, PASSWORD)
            VALUES (\'''' + username + "\',\'" + password + "\')"
    try:
        cursor.execute(query)
        connection.commit()
        query = '''
            SELECT user_id FROM USERS 
            WHERE USERNAME=\'''' + username + '''\''''
        cursor.execute(query)
        user_id = cursor.fetchone()[0]
        return user_id

    except(Exception, psycopg2.Error) as error:
        print("\nUsername already Exists", error)
        return None

def create_collection(collection_name, cursor, connection, username):
    """
    This function is used to create a collection for a user
    param collection_name: The name the user want to give to his collection
    param cursor: used to send queries to the database
    param connection: used to commit changes to the database
    param username: The username of the user
    """
    query = '''SELECT COLLECTION_ID FROM USERS
            WHERE USERNAME=\'''' + username + "\'"
    cursor.execute(query)
    doesExist = cursor.fetchone()[0]
    if(doesExist!=None):
        print("You already have a collection!")
        return

    query = '''INSERT INTO COLLECTIONS (COLLECTION_NAME)
            VALUES (\'''' + collection_name + "\')"
    cursor.execute(query)
    connection.commit()
    
    query = '''SELECT MAX(collection_id)
            FROM COLLECTIONS
            WHERE COLLECTION_NAME=\'''' + collection_name + "\'"
    cursor.execute(query)
    collection_id = cursor.fetchone()[0]

    query = '''UPDATE USERS
            SET COLLECTION_ID=''' + str(collection_id)  + '''
            WHERE USERNAME=\'''' + username + "\'"
    cursor.execute(query)
    connection.commit()


def searchSongs(songName, cursor):
    """
    This function is used to search for songs in a database
    param songName: The name of the song to be searched for
    param cursor: used to send queries to the database
    """
    query = '''SELECT TITLE, DURATION, GENRE_ID, SONG_ID FROM SONGS
            WHERE TITLE=\'''' + songName + "\'"
    cursor.execute(query)
    songList = cursor.fetchall()
    if(len(songList)==0):
        print("Song not found!")
        return
    for x in songList:
        print("Title: " + x[0] + "\nDuration: " + str(x[1]) + " ")
        query = '''SELECT NAME FROM GENRES
                WHERE GENRE_ID=''' + str(x[2])
        cursor.execute(query)
        genre = cursor.fetchone()[0]
        print("Genre: " + genre)
        query = '''SELECT NAME FROM ARTISTS
                WHERE ARTIST_ID = 
                ( SELECT ARTIST_ID FROM SONG_ARTISTS
                    WHERE SONG_ID=''' + str(x[3]) + ")"
        cursor.execute(query)
        artistName = cursor.fetchone()[0]
        print("Artist: " + artistName)
        query = '''SELECT NAME FROM ALBUMS
                WHERE ALBUM_ID = 
                ( SELECT ALBUM_ID FROM ALBUM_SONGS
                    WHERE SONG_ID=''' + str(x[3]) + ")"
        cursor.execute(query)
        albumName = cursor.fetchone()[0]
        print("Album: " + albumName)


def searchArtist(artistName, cursor):
    """
    This function is used to search for artists in a database
    param artistName: The name of the artist to be searched for
    param cursor: used to send queries to the database
    """
    query = '''SELECT NAME, ARTIST_ID FROM ARTISTS
            WHERE NAME=\'''' + artistName + "\'"
    cursor.execute(query)
    artistList = cursor.fetchall()
    if(len(artistList) == 0):
        print("Artist does not exist!")
        return
    for x in artistList:
        print("Name: " + x[0])
        print("All songs by this artist: ")
        query = '''SELECT TITLE FROM SONGS
                WHERE SONG_ID = ANY
                (SELECT SONG_ID FROM SONG_ARTISTS
                    WHERE ARTIST_ID=\'''' + str(x[1]) + "\')"
        cursor.execute(query)
        songList = cursor.fetchall()
        for y in songList:
            print("Song Title: " + y[0])


def searchAlbum(albumName, cursor):
    """
    This function is used to search for albums in a database
    param albumName: The name of the album to be searched for
    param cursor: used to send queries to the database
    """
    query = '''SELECT NAME, RELEASE_DATE, ALBUM_ID FROM ALBUMS
            WHERE NAME=\'''' + albumName + "\'"
    cursor.execute(query)
    albumList = cursor.fetchall()
    if(len(albumList) == 0):
        print("This Album does not exist!")
        return
    for x in albumList:
        print("Name: " + x[0])
        print("Release Date: " + str(x[1]))
        print("All songs in this Album: ")
        query = '''SELECT S.TITLE, A.TRACK_NUM FROM SONGS S, ALBUM_SONGS A
                WHERE S.SONG_ID = ANY
                (SELECT A.SONG_ID FROM ALBUM_SONGS
                    WHERE A.ALBUM_ID=\'''' + str(x[2]) + "\' ORDER BY ALBUM_ID)"
        cursor.execute(query)
        songList = cursor.fetchall()
        for y in songList:
            print(str(y[1]) + ": " + y[0])


def addSongColl(songName, cursor, userID, connection):
    """
    This function is used by the user to add songs to his personal collection
    param songName: The song to be added to the collection
    param cursor: used to send queries to the database to be run
    param userID: the id of the user trying to add the song to their collection
    param connection: used to commit the changes made to the database
    """
    try:
        query = '''SELECT SONG_ID FROM SONGS
            WHERE TITLE=\'''' + songName + "\'"
        cursor.execute(query)
        songIDs = cursor.fetchall()
        query = '''SELECT COLLECTION_ID FROM USERS
                WHERE USER_ID=''' + str(userID)
        cursor.execute(query)
        collectionID = cursor.fetchone()[0]
        for x in songIDs:
            query = '''INSERT INTO SONGS_IN_COLLECTIONS(SONG_ID, COLLECTION_ID)
                    VALUES (\'''' + str(x[0]) + "\',\'" + str(collectionID) + "\')"
            cursor.execute(query)
            connection.commit()
        print("Song Added to your collection!")
    except(Exception, psycopg2.Error):
        print("Song already exists in your collection!")


def addArtistColl(artistName, cursor, userID, connection):
    """
    This function is used by the user to add artists to his personal collection
    param artistName: The artist to be added to the collection
    param cursor: used to send queries to the database to be run
    param userID: the id of the user trying to add the song to their collection
    param connection: used to commit the changes made to the database
    """
    try:
        query = '''SELECT ARTIST_ID FROM ARTISTS
            WHERE NAME=\'''' + artistName + "\'"
        cursor.execute(query)
        artistIDs = cursor.fetchall()
        query = '''SELECT COLLECTION_ID FROM USERS
                WHERE USER_ID=''' + str(userID)
        cursor.execute(query)
        collectionID = cursor.fetchone()[0]
        for x in artistIDs:
            query = '''INSERT INTO ARTISTS_IN_COLLECTIONS(ARTIST_ID, COLLECTION_ID)
                    VALUES (\'''' + str(x[0]) + "\',\'" + str(collectionID) + "\')"
            cursor.execute(query)
            connection.commit()
        print("Artist added to your collection!")
    except(Exception, psycopg2.Error):
        print("Artist already exists in your collection!")


def addAlbumColl(albumName, cursor, userID, connection):
    """
    This function is used by the user to add albums to his personal collection
    param albumName: The album to be added to the collection
    param cursor: used to send queries to the database to be run
    param userID: the id of the user trying to add the song to their collection
    param connection: used to commit the changes made to the database
    """
    try:
        query = '''SELECT ALBUM_ID FROM ALBUMS
            WHERE NAME=\'''' + albumName + "\'"
        cursor.execute(query)
        albumIDs = cursor.fetchall()
        query = '''SELECT COLLECTION_ID FROM USERS
                WHERE USER_ID=''' + str(userID)
        cursor.execute(query)
        collectionID = cursor.fetchone()[0]
        for x in albumIDs:
            query = '''INSERT INTO ALBUMS_IN_COLLECTIONS(ALBUM_ID, COLLECTION_ID)
                    VALUES (\'''' + str(x[0]) + "\',\'" + str(collectionID) + "\')"
            cursor.execute(query)
            connection.commit()
        print("Album added to your collection!")
    except(Exception, psycopg2.Error):
        print("Album already exists in your collection!")


def playSong(songName, cursor, connection, userID):
    """
    This function is used when the user want to search for a song and play it
    param songName: the song the user want to play
    param cursor: used to send queries to be run
    param connection: used to commit changes to the database
    param userID: the id of the user trying to play the song
    """
    try:
        query = '''SELECT SONG_ID FROM SONGS
            WHERE TITLE=\'''' + songName + "\'"
        cursor.execute(query)
        songID = cursor.fetchone()[0]
        current = datetime.datetime.now()

        query = '''INSERT INTO PLAY_DATES (USER_ID, SONG_ID, DATE_PLAYED)
                VALUES (\'''' + str(userID) + "\',\'" + str(songID) + "\',\'" + str(current.strftime('%Y-%m-%d %H:%M:%S')) + "\')"
        cursor.execute(query)
        connection.commit()
        print("Playing " + songName + "...")
        time.sleep(5)
    except(Exception, psycopg2.Error) as error:
        print("Error playing song. Try again! ", error)
        return


def addSong(cursor, connection):
    """
    This function is used to add song to the overall database. 
    param cursor: used to send queries to the database
    param connection: used to commit changes to the database
    """
    title = input("Enter the title of the song: ")
    genre = input("Enter the Genre for the Song: ")
    duration = input("Enter the duration of the song (hh:mm:ss): ")
    artistName = input("Enter the name of the artist: ")
    albumName = input("Enter the name of the album: ")

    query = '''SELECT GENRE_ID FROM GENRES
            WHERE NAME=\'''' + genre + "\'"
    cursor.execute(query)
    genreID = cursor.fetchone()[0]

    query = '''INSERT INTO SONGS (TITLE, DURATION, GENRE_ID)
            VALUES (\'''' + title + "\',\'" + duration + "\',\'" + str(genreID) + "\')"
    cursor.execute(query)
    connection.commit()

    query = '''SELECT SONG_ID FROM SONGS
            WHERE TITLE=\'''' + title + "\'"
    cursor.execute(query)
    songID = cursor.fetchone()[0]

    query = '''SELECT ARTIST_ID FROM ARTISTS
            WHERE NAME=\'''' + artistName + "\'"
    cursor.execute(query)
    artistID = cursor.fetchone()[0]

    query = '''INSERT INTO SONG_ARTISTS (SONG_ID, ARTIST_ID)
            VALUES (\'''' + str(songID) + "\',\'" + str(artistID) + "\')"
    cursor.execute(query)
    connection.commit()

    if(albumName != "" or albumName != " "):
        query = '''SELECT ALBUM_ID FROM ALBUMS
                WHERE NAME=\'''' + albumName + "\'"
        cursor.execute(query)
        albumID = cursor.fetchone()[0]

        query = '''SELECT MAX(TRACK_NUM) FROM ALBUM_SONGS
                WHERE ALBUM_ID=''' + str(albumID)
        cursor.execute(query)
        trackNum = cursor.fetchone()[0]

        if(trackNum==None):
            trackNum = 0

        query = '''INSERT INTO ALBUM_SONGS (TRACK_NUM, ALBUM_ID, SONG_ID)
                VALUES (\'''' + str(trackNum+1) + "\',\'" + str(albumID) + "\',\'" + str(songID) + "\')"
        cursor.execute(query)
        connection.commit()

    print("Song \'" + title + "\' was added to the database successfully")


def addAlbum(cursor, connection):
    """
    This function is used to add album to the overall database. 
    param cursor: used to send queries to the database
    param connection: used to commit changes to the database
    """
    name = input("Enter the name of the album: ")
    release_date = datetime.datetime.today()
    artistName = input("Enter the name of the Artist: ")

    query = '''INSERT INTO ALBUMS (NAME, RELEASE_DATE)
            VALUES (\'''' + name + "\',\'" +  str(release_date.strftime('%Y-%m-%d')) + "\')"
    cursor.execute(query)
    connection.commit()

    query = '''SELECT ARTIST_ID FROM ARTISTS
            WHERE NAME=\'''' + artistName + "\'"
    cursor.execute(query)
    artistID = cursor.fetchone()[0]

    query = '''SELECT ALBUM_ID FROM ALBUMS
            WHERE NAME=\'''' + name + "\'"
    cursor.execute(query)
    albumID = cursor.fetchone()[0]

    query = '''INSERT INTO ALBUM_ARTISTS (ALBUM_ID, ARTIST_ID)
            VALUES (\'''' + str(albumID) + "\',\'" + str(artistID) + "\')"
    cursor.execute(query)
    connection.commit()

    print("Album \'" + name + "\' was added to the database successfully")


def addArtist(cursor, connection):
    """
    This function is used to add artist to the overall database. 
    param cursor: used to send queries to the database
    param connection: used to commit changes to the database
    """
    name = input("Enter the name of the artist: ")

    query = '''INSERT INTO ARTISTS (NAME)
            VALUES (\'''' + name +  "\')"
    cursor.execute(query)
    connection.commit()
    print("Artist \'" + name + "\' was added to the database successfully")



if __name__ == "__main__":
    """
    The main function. This takes commands from the users and calls the 
    respective functions to carry out the operation
    """
    sql_connection, sql_cursor = connect()
    print("\nWelcome to Music Player by Straigh Outta Database!")
    user_id = 0
    username = ""
    #Signup or Login
    while True:
        initial = input("\nEnter 'login', 'signup', 'add to database' or 'quit': ")
        if(initial=='login'):
            username = input("\nUsername: ")
            password = input("Password: ")
            user_id = login(username, password, sql_cursor)
            if(user_id!=None):
                break
            else:
                continue
        elif(initial=='signup'):
            username = input("\nEnter a username: ")
            password = input("\nEnter a password: ")
            user_id = signup(username, password, sql_cursor, sql_connection)
            if(user_id!=None):
                break
            else:
                continue
        elif(initial == "add to database"):
            while True:
                command2 = input("Enter 'song', 'album' or 'artist' to add to the database: ")
                if( command2 == "song"):
                    addSong(sql_cursor, sql_connection)
                    break
                elif (command2 == "album"):
                    addAlbum(sql_cursor, sql_connection)
                    break
                elif (command2 == "artist"):
                    addArtist(sql_cursor, sql_connection)
                    break
                else:
                    print("Incorrect command, please try again!")
                    continue
        elif(initial == "quit"):
            print("Application Closed Successfully")
            close(sql_connection, sql_cursor)
            exit(0)
        else:
            print("Wrong command, Try again!")
    
    while True:
        command = input("\nEnter a command (type 'help' for help): ")
        if(command == "help"):
            help()
        elif(command == "create collection"):
            collection_name = input("\nEnter a name for your Collection: ")
            create_collection(collection_name, sql_cursor, sql_connection, username)
            print("\nCollection Created")
        elif(command == "search"):
            while True:
                command2 = input("\nEnter 'song', 'artist' or 'album': ")
                if(command2 == "song"):
                    songName = input("Enter Name of Song: ")
                    searchSongs(songName, sql_cursor)
                    break
                elif(command2 == "artist"):
                    artistName = input("Enter Name of Artist: ")
                    searchArtist(artistName, sql_cursor)
                    break
                elif(command2 == "album"):
                    albumName = input("Enter Name of Album: ")
                    searchAlbum(albumName, sql_cursor)
                    break
                else:
                    print("Incorrect Command! Try Again!")
                    continue
        elif(command == 'collection add'):
            while True:
                command2 = input("\nEnter 'song', 'artist' or 'album': ")
                if(command2 == "song"):
                    songName = input("Enter Name of Song: ")
                    addSongColl(songName, sql_cursor, user_id, sql_connection)
                    break
                elif(command2 == "artist"):
                    artistName = input("Enter Name of Artist: ")
                    addArtistColl(artistName, sql_cursor, user_id, sql_connection)
                    break
                elif(command2 == "album"):
                    albumName = input("Enter Name of Album: ")
                    addAlbumColl(albumName, sql_cursor, user_id, sql_connection)
                    break
                else:
                    print("Incorrect Command! Try Again!")
                    continue
        elif(command=="play"):
            songName = input("Enter the name of the song to be played: ")
            playSong(songName, sql_cursor, sql_connection, user_id)
        elif(command=='quit'):
            print("\nApplication Closed Successfully")
            break
        else:
            print("\nIncorrect command")
            help()
            print("\nTry Again")

    close(sql_connection, sql_cursor)
