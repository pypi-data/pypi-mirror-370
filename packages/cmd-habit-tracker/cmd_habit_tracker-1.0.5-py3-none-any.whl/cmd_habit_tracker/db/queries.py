from cmd_habit_tracker.utils import data as db

################################### Initialization queries ###################################

def habits_table_creation_query():
    """
    period should store an integer indicating the number of days that the app should track a habit
    """
    return f"""
    CREATE TABLE IF NOT EXISTS {db.Tables.HABITS} (
        {db.Habits.ID} INTEGER PRIMARY KEY AUTOINCREMENT,
        {db.Habits.TITLE} TEXT NOT NULL,
        {db.Habits.START_DATE} DATE NOT NULL,
        {db.Habits.PERIOD} INTEGER,
        {db.Habits.NOTE} TEXT NOT NULL,
        {db.Habits.FREQUENCY_FORMAT} INTEGER NOT NULL,
        {db.Habits.FREQUENCY_AMOUNT} INTEGER NOT NULL,
        {db.Habits.TARGET_METRIC} TEXT,
        {db.Habits.TARGET_AMOUNT} INTEGER
    );
    """

def tracker_table_creation_query():
    return f"""
    CREATE TABLE IF NOT EXISTS {db.Tables.TRACKER} (
        {db.Tracker.ID} INTEGER PRIMARY KEY,
        {db.Tracker.HABIT_ID} INTEGER,
        {db.Tracker.DATE} DATE NOT NULL,
        {db.Tracker.ACHIEVED} INTEGER NOT NULL,
        {db.Tracker.EXPLANATION} TEXT,
        FOREIGN KEY ({db.Tracker.HABIT_ID}) REFERENCES {db.Tables.HABITS}(id)
    );
    """


def archived_habits_table_creation_query():
    return f"""
    CREATE TABLE IF NOT EXISTS {db.Tables.ARCHIVED_Habits} (
        {db.Habits.ID} INTEGER PRIMARY KEY,
        {db.Habits.TITLE} TEXT NOT NULL,
        {db.Habits.START_DATE} DATE NOT NULL,
        {db.Habits.PERIOD} INTEGER,
        {db.Habits.NOTE} TEXT NOT NULL,
        {db.Habits.FREQUENCY_FORMAT} INTEGER NOT NULL,
        {db.Habits.FREQUENCY_AMOUNT} INTEGER NOT NULL,
        {db.Habits.TARGET_METRIC} TEXT,
        {db.Habits.TARGET_AMOUNT} INTEGER
    );
    """
def archived_tracker_table_creation_query():
    return f"""
    CREATE TABLE IF NOT EXISTS {db.Tables.ARCHIVED_TRACKER} (
        {db.Tracker.ID} INTEGER PRIMARY KEY,
        {db.Tracker.HABIT_ID} INTEGER,
        {db.Tracker.DATE} DATE NOT NULL,
        {db.Tracker.ACHIEVED} INTEGER NOT NULL,
        {db.Tracker.EXPLANATION} TEXT,
        FOREIGN KEY ({db.Tracker.HABIT_ID}) REFERENCES {db.Tables.ARCHIVED_Habits}(id)
    );
    """


################################### Risky queries ###################################


def drop_tables_query():
    """Warning: Deletes all the data"""
    return f"""
    DROP TABLE {db.Tables.TRACKER};
    DROP TABLE {db.Tables.HABITS};
    """

################################### Habits queries ###################################

def get_habit_query():
    """parameters are: :id"""
    return f"""
    SELECT * FROM {db.Tables.HABITS}
    WHERE {db.Habits.ID}=:id
    """
def get_habit_by_title_query():
    return f"""
    SELECT * FROM {db.Tables.HABITS}
    WHERE {db.Habits.TITLE}=:{db.Habits.TITLE}
    """

def get_all_habits_query():
    return f"""
    SELECT * FROM {db.Tables.HABITS}
    """

def add_habit_query():
    """parameters are: (see tools.Habits)"""
    return f"""
    INSERT INTO {db.Tables.HABITS} ({db.Habits.TITLE}, {db.Habits.START_DATE}, {db.Habits.PERIOD}, {db.Habits.NOTE}, {db.Habits.FREQUENCY_AMOUNT}, {db.Habits.FREQUENCY_FORMAT}, {db.Habits.TARGET_METRIC}, {db.Habits.TARGET_AMOUNT})
    VALUES (:{db.Habits.TITLE}, (SELECT date()), :{db.Habits.PERIOD}, :{db.Habits.NOTE}, :{db.Habits.FREQUENCY_AMOUNT}, :{db.Habits.FREQUENCY_FORMAT}, :{db.Habits.TARGET_METRIC}, :{db.Habits.TARGET_AMOUNT});
    """

def get_habits_by_title():
    return f"""
    SELECT * FROM {db.Tables.HABITS}
    WHERE {db.Habits.TITLE}=:{db.Habits.TITLE}
    """
def delete_habit_query():
    return f"""
    DELETE FROM {db.Tables.HABITS}
    WHERE {db.Habits.ID}=:{db.Habits.ID}
    """

################################### Tracking queries ###################################


def get_track_info_of_date_query():
    return f"""
    SELECT * FROM {db.Tables.TRACKER}
    WHERE {db.Tracker.DATE}=:{db.Tracker.DATE}
    """

def add_track_query():
    return f"""
    INSERT INTO {db.Tables.TRACKER} ({db.Tracker.HABIT_ID}, {db.Tracker.DATE}, {db.Tracker.ACHIEVED}, {db.Tracker.EXPLANATION})
    VALUES (:{db.Tracker.HABIT_ID}, :{db.Tracker.DATE}, :{db.Tracker.ACHIEVED}, :{db.Tracker.EXPLANATION})
    """

def delete_all_tracking_info_by_date():
    return f"""
    DELETE FROM {db.Tables.TRACKER}
    WHERE {db.Tracker.DATE}=:{db.Tracker.DATE}
    """

def refresh_tracking_table_query():
    return f"""
    DELETE FROM {db.Tables.TRACKER}
    WHERE {db.Tracker.HABIT_ID} NOT IN (SELECT {db.Habits.ID} FROM {db.Tables.HABITS})
    """

################################### Advanced queries ###################################

def get_all_tracking_info_of_a_month():
    """
    params:
        first - a date of the first day in the month
        last - ...
    """
    return f"""
    SELECT * FROM {db.Tables.TRACKER}
    WHERE  {db.Tracker.DATE}>=:first and {db.Tracker.DATE}<=:last
    ORDER BY {db.Tracker.DATE}
    """