from __future__ import annotations

from src.pyDataCube.engines.postgres import postgres
from src.pyDataCube.session.session import *

DATABASE_USER = "sigmundur"
DATABASE_PASSWORD = ""
DATABASE_HOST = "127.0.0.1"
DATABASE_PORT = "5432"
DATABASE_NAME = "ssb_snowflake_dev"

postgres_engine: Postgres = postgres(DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
postgres = create_session(postgres_engine)
view = postgres.load_view('lineorder')
print(view.day.year.attributes)
print(view.measures)

# # converter = QB4OLAPExport(view.cube, "./output.ttl")
# # converter.export()
# importer = QB4OLAPImporter("output.ttl", postgres_engine)
# session = importer.importer()
# view2: View = session.load_view("lineorder")
# # validator = Validator(view.cube._metadata)
# # result = validator.validate_qb()

mere_view = view.columns(view.day.month.mo_month.members()) \
    .rows(view.part.brand1.b_brand1.members()) \
    .pages(view.day.day.d_daynuminweek.members())
result100 = mere_view.output()

hej = 1
# view42 = view.columns(view.day.month.mo_month.members())
# output42 = view42.output()
#
# view.lo_quantity.set_aggregate_function("avg")
#
# view9 = view.columns(view.day.year.y_year[1997].children())\
#             .rows(view.part.category.ca_category.members())\
#             .pages([view.customer.city.ci_city["UNITED ST9"]])\
#             .where((view.day.day.d_daynuminmonth <= 7)
#                     & ((view.supplier.nation.n_nation == "MOZAMBIQUE")
#                         | (view.supplier.nation.n_nation == "RUSSIA")))\
#             .using(view.lo_quantity,
#                    lost_income=view.lo_extendedprice * view.lo_discount)
#
# urslit = view9.output()
#
# test = view.day.year.y_year[1997]
# test2 = test.children()
# view.day.month.mo_month.set_sort_key(view.day.month.mo_yearmonth)
# test3 = test.children()
#
# hej = 1
#
mere_view = view.columns(view.day.month.mo_month.members()) \
    .rows(view.part.category.ca_category.members()) \
    .pages(view.day.year.y_year.members()) \
    .using(view.lo_quantity, view.lo_tax)
result_uden_order = mere_view.output()

hej = 1
# view.day.month.mo_month.set_sort_key(view.day.month.mo_yearmonthnum)
#
# mere_view = view.columns(view.day.month.mo_month.members()) \
#     .rows(view.part.category.ca_category.members()) \
#     .pages(view.day.year.y_year.members()) \
#     .using(view.lo_quantity, view.lo_tax)
# result_med_order = mere_view.output()
#
# hej = 1
#

city = view.customer.city.ci_city.members()[0]

new_view = view \
  .axis(0, view.day.year.y_year[1992].children())\
  .axis(1, view.part.category.ca_category.members())\
  .axis(2, [view.customer.city.ci_city.members()[0]])\
  .where((view.day.day.d_daynuminmonth <= 7)
         & ((view.supplier.nation.n_nation == "ARGENTINA")
            | (view.supplier.nation.n_nation == "FRANCE")))\
  .using(view.lo_revenue,
            lost_income=
              view.lo_extendedprice * view.lo_discount)

# new_view2 = view \
#     .axis(0, view.day.year.y_year[1992].children()) \
#     .axis(1, view.part.category.ca_category.members()) \
#     .axis(2, [city]) \
#     .where((view.day.day.d_daynuminmonth <= 7)
#            & ((view.supplier.nation.n_nation == "CANADA")
#               | (view.supplier.nation.n_nation == "JAPAN"))) \
#     .using(view.lo_revenue,
#            lost_income=
#            view.lo_extendedprice * view.lo_discount)

article_result = new_view.output()
# check_result = new_view2.output()

# # view.delete_measure(view.lo_revenue)
#
hej = 1
#
# # result2 = view.output()
#
# view9 = view.where(
#     (view.day.year.y_year == 1993)
#     & (view.lo_discount > 0)
#     & (view.lo_discount < 4)
#     & (view.lo_quantity < 25)) \
#     .using(revenue=view.lo_extendedprice * view.lo_discount)
#
# result2 = view9.output()
#
#
# hej = 1
#
# # test = view.output()
#
# # test10 = view.part.category.ca_category["MFGR#44"]["MFGR#4427"]
# # test11 = view.day.day.d_dayofweek.Thursday
# #
# # test1 = view.day.month.mo_month.members()
# # test1 = view.day.year.y_year[1992].January
# # test2 = [x for xs in [i.children() for i in test1] for x in xs]
#
# view10 = view.columns(view.day.month.mo_month.members()) \
#              .rows(view.part.part.p_name.members()) \
#              .using(view.lo_revenue)
# result10 = view10.output()
#
# view3 = view.columns(view.day.year.y_year.members()) \
#             .rows(view.part.brand1.b_brand1.members()) \
#             .where((view.part.category.ca_category == "MFGR#12") &
#                    (view.supplier.region.r_region == "AMERICA")) \
#             .using(view.lo_revenue, revenue=view.lo_extendedprice * view.lo_discount)
# result = view3.output()
#
# test = view.columns(view.customer.city.ci_city.members()) \
#             .rows(view.supplier.city.ci_city.members()) \
#             .pages(view.day.year.y_year.members()) \
#             .using(view.lo_revenue)
# result2 = test.output()
#
# view4 = view.columns(view.day.month.mo_month.members())
# result3 = view4.output()
#
# hej = 1
#
# # ## ssb query 2.1
# # view.columns(view.date.year.y_year.members()) \
# #     .rows(view.part.brand1.b_brand1.members()) \
# #     .where(view.part.category.ca_category = "MFGR#12" &
# #            view.supplier.region.r_region = "AMERICA") \
# #     .measures(view.lo_revenue)
#
#
# # print()
# # print("Measures: ", cube.measures())
# # print("Dimensions: ", cube.dimensions())
# # print("Date hierarchy: ", cube.date.hierarchies())
# # print("Supplier name dictionary: ", cube.supplier.supplier_name.__dict__)
# # print("Date dimension dictionary: ", cube.date.__dict__)
# # print("Date year level dictionary: ", cube.date.date_year.__dict__)
# # print("2022 Level member: ", cube.date.date_year["2022"]["January"])
#
# # print("Output of the cube (cube): ", cube.output())
# # print("Date dimension current level: ", cube._dimension_list[1].current_level)
# # c1 = cube._drill_down(cube.date)
# # print("Date dimension current level: ", c1._dimension_list[1].current_level)
# # print("c1 dictionary: ", c1.__dict__)
# # print("Output of the cube (c1): ", c1.output())
#
# # c2 = c1._drill_down(c1.date)
# # print("Cube (c2) dictionary: ", c2.date.__dict__)
# # c3 = c2._slice(c2.date, c2.date.date_year._2022._January)
# # print(c3._dimension_list[1].__dict__)
#
#
# # print(c2._dimension_list[1].current_level)
# # c3 = c2._roll_up(c2.date)
# # print(c3._dimension_list[1].current_level)
# # c4 = c3._roll_up(c3.date)
# # print(c4._dimension_list[1].current_level)
#
#
# # print("Date dimension dictionary: ", cube.date.__dict__)
# # cube.date._roll_up()
# # print("Date dimension dictionary: ", cube.date.__dict__)
#
# # print("2022 Level member dictionary: ", cube.date.date_year._2022.__dict__)
# # print("January Level member dictionary: ", cube.date.date_year._2022._January.__dict__)
# # print("Day 1 Level member dictionary: ", cube.date.date_year._2022._January._1.__dict__)
#
# # ## Supplier testing
# # print("Supplier hierarchy: ", cube.supplier.hierarchies())
# # print("Nation dictionary: ", cube.supplier.supplier_nation.__dict__)
# # print("Denmark dictionary: ", cube.supplier.supplier_nation._Denmark.__dict__)
#
#
# # cube.columns([cube.date.date_year._2022._January])
# # print("The output: ", cube.output())
#
#
# # print()
# # print(cube.store.store_address["Jyllandsgade 1"])
# # print(cube.store.store_address["Jyllandsgade 2"])
# #
# # cube.where(cube.supplier.supplier_nation == "Denmark" and cube.store.store_address == "Jyllandsgade 1")
#
#
#
# # conn = psycopg2.connect(
# #     dbname="salesdb_snowflake_test",
# #     user="sigmundur",
# #     password=""
# # )
#
#
# # # Cube -> View syntactic suger not implemented
# # view._axes = []
# # view = view.axis(0, view.cube.date.date_month.members())
#
#
# # output = view.output()
# # print(output)
# # with conn:
# #     with conn.cursor() as curs:
# #         curs.execute(output)
# #         print(curs.fetchall())
#
#
# def generate_data():
#     supplier = 1221
#     store = 4444
#     product = 9012
#     total_sales_price = np.random.randint(10, high=1000, size=721)
#     unit_sales = np.random.randint(1, high=20, size=721)
#     sale_date = [i for i in range(1, 722)]
#
#     with open("/home/sigmundur/test/test.csv", "w") as out:
#         csv_out = csv.writer(out)
#         for i in range(len(sale_date)):
#             csv_out.writerow((supplier, store, product, sale_date[i], total_sales_price[i], unit_sales[i]))
#