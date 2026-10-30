import csv
from decimal import Decimal
import ecommerce_app as app


def run_test(row):
    tc_id = row["Test_Case_ID"].strip()
    data = row["Test_Data"].strip()
    expected = row["Expected_Result"].strip()

    catalog = app.Catalog()
    cart = app.Cart(catalog)

    try:
        # REQ-01: Product availability
        if tc_id == "TC-01":
            product = catalog.get(data)
            actual = f"Trả về {product.title}"
            assert actual == expected, actual
            return "PASS", actual

        elif tc_id == "TC-02":
            try:
                catalog.get(data)
            except ValueError as exc:
                actual = str(exc)
                assert actual == expected, actual
                return "PASS", actual
            raise AssertionError("Expected PRODUCT_UNAVAILABLE")

        elif tc_id == "TC-03":
            catalog.products["A"].active = False
            try:
                catalog.get("A")
            except ValueError as exc:
                actual = str(exc)
                assert actual == expected, actual
                return "PASS", actual
            raise AssertionError("Expected PRODUCT_UNAVAILABLE")

        # REQ-02: Cart quantity
        elif tc_id == "TC-04":
            cart.add("A", 2)
            actual = cart.lines[0].quantity
            assert actual == 2, actual
            return "PASS", f"Cart có A với quantity={actual}"

        elif tc_id == "TC-05":
            try:
                cart.add("A", 0)
            except ValueError as exc:
                actual = str(exc)
                assert actual == expected, actual
                return "PASS", actual
            raise AssertionError("Expected INVALID_QUANTITY")

        elif tc_id == "TC-06":
            cart.add("A", 2)
            cart.add("A", 3)
            actual = cart.lines[0].quantity
            assert actual == 5, actual
            return "PASS", f"Cart có A với quantity={actual}"

        # REQ-03: Subtotal
        elif tc_id == "TC-07":
            cart.add("A", 2)
            actual = cart.subtotal()
            assert actual == Decimal("400000"), actual
            return "PASS", f"Subtotal={actual}"

        elif tc_id == "TC-08":
            cart.add("A", 1)
            cart.add("B", 1)
            actual = cart.subtotal()
            assert actual == Decimal("500000"), actual
            return "PASS", f"Subtotal={actual}"

        elif tc_id == "TC-09":
            cart.add("C", 3)
            actual = cart.subtotal()
            assert actual == Decimal("450000"), actual
            return "PASS", f"Subtotal={actual}"

        # REQ-09: Shipping
        elif tc_id == "TC-10":
            actual = app.Shipping().calculate(
                Decimal("500000"), "inner"
            )
            assert actual == Decimal("0"), actual
            return "PASS", f"Shipping={actual}"

        elif tc_id == "TC-11":
            actual = app.Shipping().calculate(
                Decimal("300000"), "inner"
            )
            assert actual == Decimal("30000"), actual
            return "PASS", f"Shipping={actual}"

        elif tc_id == "TC-12":
            actual = app.Shipping().calculate(
                Decimal("300000"), "outer"
            )
            assert actual == Decimal("50000"), actual
            return "PASS", f"Shipping={actual}"

        # REQ-14: Empty cart integrity
        elif tc_id == "TC-13":
            checkout = app.Checkout(catalog)
            customer = app.Customer("CUST-01")

            try:
                checkout.place(customer, cart)
            except ValueError as exc:
                actual = str(exc)
                assert actual == expected, actual
                return "PASS", actual

            raise AssertionError("Expected EMPTY_CART")

        elif tc_id == "TC-14":
            cart.add("A", 1)
            checkout = app.Checkout(catalog)
            customer = app.Customer("CUST-01")
            order = checkout.place(customer, cart)

            assert order.order_id, "No order was created"
            return "PASS", f"Checkout tạo order {order.order_id}"

        elif tc_id == "TC-15":
            checkout = app.Checkout(catalog)
            customer = app.Customer("CUST-01")

            try:
                checkout.place(customer, cart, voucher="SAVE10")
            except ValueError as exc:
                actual = str(exc)
                assert actual == expected, actual
                return "PASS", actual

            raise AssertionError("Expected EMPTY_CART")

        else:
            raise NotImplementedError(
                f"Unknown test case: {tc_id}"
            )

    except Exception as exc:
        return "FAIL", str(exc)


def run_suite(csv_path="STLab02_EduCommerce_TestCases.csv"):
    results = []

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            status, actual = run_test(row)

            results.append({
                "Test_Case_ID": row["Test_Case_ID"],
                "Requirement_ID": row["Requirement_ID"],
                "Scenario_ID": row["Scenario_ID"],
                "Test_Case": row["Test_Case"],
                "Test_Data": row["Test_Data"],
                "Expected_Result": row["Expected_Result"],
                "Actual_Result": actual,
                "Status": status
            })

    if not results:
        raise ValueError("CSV không có test case nào.")

    report_path = "STLab02_Test_Execution_Report.csv"

    with open(report_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    for result in results:
        print(
            f'{result["Test_Case_ID"]} '
            f'{result["Status"]} - '
            f'{result["Actual_Result"]}'
        )

    passed = sum(r["Status"] == "PASS" for r in results)
    failed = sum(r["Status"] == "FAIL" for r in results)

    print(
        f"\nTotal: {len(results)} | "
        f"PASS: {passed} | FAIL: {failed}"
    )
    print(f"Report saved: {report_path}")

    return results
