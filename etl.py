import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    '''
    This procedure process songs files, reading, transforming 
    and inserting on database.

    It extracts the artist and song information in order to store 
    it into the artists and the songs tables.

    Parameters
    ----------
    cur : psycopg2.connection.cursor
        The database connection cursor for execute insertion queries
    
    filepath : string
        The string of songs file path
    '''

    # open song file
    df = pd.read_json(filepath, typ='series')
    
    # insert artist record
    artist_data = df[[
        'artist_id', 
        'artist_name', 
        'artist_location', 
        'artist_latitude', 
        'artist_longitude'
    ]].values.tolist()
    cur.execute(artist_table_insert, artist_data)

    # insert song record
    song_data = df[['song_id', 'title', 'artist_id', 'year', 'duration']].values.tolist()
    cur.execute(song_table_insert, song_data)


def process_log_file(cur, filepath):
    '''
    This procedure process logs files, reading, transforming 
    and inserting on database.
    
    It extracts the date, user and songplay information in order 
    to store it into the time, users and songplayes tables. 

    Parameters
    ----------
    cur : psycopg2.connection.cursor
        The database connection cursor for execute insertion queries
    
    filepath : string
        The string of logs file path
    '''

    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df.page == 'NextSong']

    """
    create a new dataframe converting timestamp column to datetime in a new column 
    and keeping the original value
    """ 
    t = pd.DataFrame()
    t['ts'] = df['ts']
    t['tsc'] = df['ts'].apply(lambda ts: pd.to_datetime(ts, unit='ms'))
    
    # insert time data records
    time_data = ([
        t.ts, 
        t.tsc.dt.hour, 
        t.tsc.dt.day, 
        t.tsc.dt.week, 
        t.tsc.dt.month, 
        t.tsc.dt.year, 
        t.tsc.dt.weekday
    ])
    column_labels = ('start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday')
    
    time_df = pd.DataFrame(time_data, index=column_labels).transpose()

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]

    # insert user records
    for i, row in user_df.iterrows():
        try:
            cur.execute(user_table_insert, row)
        except psycopg2.Error as err:
            print(err)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        if songid and artistid:
            songplay_data = (row.ts, row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent)
            cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    '''
    This procedure read and execute a process for all kinds file 
    inside path. To do it, the procedure executing a specific 
    function to process a specific kind of file. These files can be
    `songs` or  `logs` file.

    Parameters
    ----------
    cur : psycopg2.connection.cursor
        The database connection cursor

    conn : psycopg2.connection
        The database connection
    
    filepath : string
        The string of path containing a kind of files
    
    func : function
        The function called to process files in a specific path
    '''

    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))

    print('data process finished.')

def main():
    '''
    This is the main procedure. The start point of the ETL process.
    Here the connection to the database is opened, the file paths are defined
    and the execution starts.
    '''
    conn = psycopg2.connect("host=postgres dbname=sparkifydb user=postgres password=example")
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()