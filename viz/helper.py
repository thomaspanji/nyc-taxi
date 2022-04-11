# HELPER
def filter_dataframe(df, vendor, payment, passenger):
    if payment is not None:
        dff = df[df['vendor'].isin(vendor)
                & df['payment'].isin(payment)
                & (df['passenger_count'] >= passenger[0]) 
                & (df['passenger_count'] <= passenger[1])]
        return dff
    else:
        dff = df[df['vendor'].isin(vendor)
                & (df['passenger_count'] >= passenger[0]) 
                & (df['passenger_count'] <= passenger[1])]
        return dff