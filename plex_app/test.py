

from main import app
import pandas as pd
from db_utils import init_db, get_connection

test_df_file = 'current_dls.csv'

def main_test():
    conn = get_connection()
    df = pd.read_csv(test_df_file,index_col=0)
    init_db()
    df.to_sql('available_dls',conn, if_exists='replace', index=False)
    app.run(debug=True)

if __name__ == '__main__':
    main_test()