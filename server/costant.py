greetings = [
    "Hello",
    "Hi there",
    "Good morning",
    "Good afternoon",
    "Good evening",
    "It’s nice to meet you",
    "It’s a pleasure to meet you",
    "How may I help you"
]

faqBlob = """1. Are you delivering non-essential products?
As per government guidelines, we are accepting orders for all products across the country. In the event any location is designated as a restricted zone under regulations, we may limit orders to essential products.
2. Can I place orders using Pay on Delivery (Cash/SMS Pay link)?
We are accepting Cash/Pay on Delivery in most locations where we are delivering all products. If your location is eligible for Pay on Delivery, you will see the option on the payment page while placing your order. If the chosen delivery location is designated as a restricted zone, we will continue to accept only pre-paid orders for such locations.For more information on steps taken to maintain social distancing at delivery, please visit this page.
3. I have already placed an order, but it is showing a long delivery date?
We are working across the Operations network to enable faster deliveries to customers, while ensuring safety of associates and customers. We are continuously improving our delivery promise to offer a seamless delivery experience. We are following the latest Government guidelines to enable delivery of essentials and non-essentials in all permitted areas, and the delivery timeline may be impacted due to local restrictions.
4. Can I still create returns for my orders?
Yes, you can create returns by visiting Your Orders. However, the return pick up timeline may be longer than usual if movement of goods and person is restricted in your area, by local or state government.
5. What is No-Contact delivery?
Amazon is focused on the health and safety of our customers and employees. Based on regional regulations and social distancing requirements; there is a change to the way we’re delivering your items. To adhere to the contactless or no-contact delivery, the delivery associate will leave your order at your doorstep and maintain a 2-meter distance.Learn more about what we are doing to ensure the safety of our employees, associates, delivery and transportation partners here.
6. What is Amazon doing to keep customers and employees safe?
Customer safety is of utmost importance to us and we are closely monitoring the impact of COVID-19. Learn more about what we are doing to ensure the safety and support of our customers, communities, and employees during this difficult time on the Amazon Day 1 blog here."""

lines = faqBlob.split('\n')
qus = []
ans = []
for lineId in range(0, len(lines), 2):
  qus.append(lines[lineId][2:])
  ans.append(lines[lineId+1])