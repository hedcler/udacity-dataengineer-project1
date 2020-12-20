# DROP TABLES
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"


# CREATE TABLES
songplay_table_create = ("""
CREATE TABLE songplays (
    songplay_id SERIAL PRIMARY KEY, 
    start_time bigint, 
    user_id bigint, 
    level varchar, 
    song_id varchar, 
    artist_id varchar, 
    session_id int, 
    location varchar, 
    user_agent varchar,
    UNIQUE (start_time, user_id, song_id, artist_id, session_id)
)

""")

user_table_create = ("""
CREATE TABLE users (
    user_id bigint PRIMARY KEY, 
    first_name varchar, 
    last_name varchar, 
    gender char, 
    level varchar
)
""")

song_table_create = ("""
CREATE TABLE songs 
(
    song_id varchar PRIMARY KEY, 
    title varchar, 
    artist_id varchar, 
    year int, 
    duration float
)
""")

artist_table_create = ("""
CREATE TABLE artists (
    artist_id varchar PRIMARY KEY, 
    name varchar, 
    location varchar, 
    latitude float, 
    longitude float
)
""")

time_table_create = ("""
CREATE TABLE time (
    start_time bigint PRIMARY KEY, 
    hour int, 
    day int, 
    week int, 
    month varchar, 
    year int, 
    weekday varchar
)
""")

# INSERT RECORDS
songplay_table_insert = ("""
INSERT INTO songplays 
(start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
""")

user_table_insert = ("""
INSERT INTO users 
(user_id, first_name, last_name, gender, level)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (user_id) 
DO UPDATE
    SET first_name = COALESCE(users.first_name, EXCLUDED.first_name), 
        last_name = COALESCE(users.last_name, EXCLUDED.last_name), 
        gender = COALESCE(users.gender, EXCLUDED.gender), 
        level = COALESCE(users.level, EXCLUDED.level);
""")

song_table_insert = ("""
INSERT INTO songs 
(song_id, title, artist_id, year, duration)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (song_id) 
DO NOTHING
""")

artist_table_insert = ("""
INSERT INTO artists 
(artist_id, name, location, latitude, longitude)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (artist_id) 
DO UPDATE
    SET location = COALESCE(artists.location, EXCLUDED.location), 
        latitude = COALESCE(artists.latitude, EXCLUDED.latitude), 
        longitude = COALESCE(artists.longitude, EXCLUDED.longitude);
""")


time_table_insert = ("""
INSERT INTO time
(start_time, hour, day, week, month, year, weekday)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
""")

# FIND SONGS
# find the song ID and artist ID based on the title, artist name, and duration of a song
# start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
song_select = ("""
SELECT s.song_id as songid, s.artist_id as artistid
FROM songs s
JOIN artists a ON a.artist_id = s.artist_id
WHERE s.title = %s
AND a.name = %s
AND s.duration = %s
""")

# QUERY LISTS

create_table_queries = [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]