def get_df_by_type(places_df, pop_times_df, place_type):
    places_by_type = places_df[places_df.type == place_type]
    pop_times_by_type = pop_times_df[pop_times_df.place_id.isin(places_by_type.place_id)]
    return places_by_type, pop_times_by_type
