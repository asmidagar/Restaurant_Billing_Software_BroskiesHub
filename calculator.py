def calculate_total(price, gst, qty, discount_percent):
    price_with_gst = price + (price * gst / 100)
    total_price = price_with_gst * qty

    if discount_percent > 0:
        discount_amount = total_price * (discount_percent / 100)
        total_price -= discount_amount

    return round(price_with_gst, 2), round(total_price, 2)
