create table transactions (
    order_id int primary key,
    service_option VARCHAR(30),
    payment_method VARCHAR(40),
    total_price int,
    total_gst int,
    grand_total int
)

update transactions set grand_total = total_price + total_gst;

ALTER TABLE transactions ADD COLUMN payment_mode TEXT;
