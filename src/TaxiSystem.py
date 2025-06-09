from typing import List, Optional, Dict
import datetime
import math


class DriverAssignmentStrategy:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DriverAssignmentStrategy, cls).__new__(cls)
        return cls._instance

    def is_peak_hour(self) -> bool:
        current_time = datetime.datetime.now().time()
        morning_peak = datetime.time(7, 0) <= current_time <= datetime.time(10, 0)
        evening_peak = datetime.time(17, 0) <= current_time <= datetime.time(20, 0)
        return morning_peak or evening_peak

    def select_driver(
        self, drivers: List["Driver"], order: "Order"
    ) -> Optional["Driver"]:
        if not drivers:
            return None

        if self.is_peak_hour():
            return min(
                drivers,
                key=lambda d: self.calculate_distance(
                    d.x, d.y, order.pickup.x, order.pickup.y
                ),
            )
        else:
            return min(
                drivers,
                key=lambda d: self.calculate_distance(
                    d.x, d.y, order.pickup.x, order.pickup.y
                )
                * abs(d.rating - order.client_rating),
            )

    @staticmethod
    def calculate_distance(
        driver_x: float, driver_y: float, order_x: float, order_y: float
    ) -> float:
        return abs(driver_x - order_x) + abs(driver_y - order_y)


class OrderSubject:
    def __init__(self):
        self._observers: List[Driver] = []

    def attach(self, observer: "Driver"):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: "Driver"):
        self._observers.remove(observer)

    def notify(self, order: "Order", selected_driver_id: int):
        for observer in self._observers:
            if observer.is_available and observer.driver_id == selected_driver_id:
                observer.update(order)


class MapPoint:
    def __init__(self, id: int, name: str, x: float, y: float):
        self.id = id
        self.x = x
        self.y = y
        self.name = name


class Driver:
    def __init__(
        self,
        driver_id: int,
        name: str,
        current_location: str = "default",
        x: float = 0,
        y: float = 0,
        rating: float = 5.0,
    ):
        self.driver_id = driver_id
        self.name = name
        self.is_available = True
        self.current_order: Optional["Order"] = None
        self.current_location = current_location
        self.x = x
        self.y = y
        self.rating = rating

    def update(self, order: "Order"):
        if self.is_available:
            print(f"Водитель {self.name} получил уведомление о заказе {order.order_id}")

    def set_location(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def end_order(self):
        pass


class Car:
    def __init__(self, car_id: int, model: str, license_plate: str):
        self.car_id = car_id
        self.model = model
        self.license_plate = license_plate


class Order:
    def __init__(
        self,
        order_id: int,
        client_id: int,
        pickup: MapPoint,
        destination: MapPoint,
        client_rating: float = 5.0,
    ):
        self.order_id = order_id
        self.client_id = client_id
        self.pickup = pickup
        self.destination = destination
        self.status = "pending"  # pending, in_progress, completed
        self.driver: Optional[Driver] = None
        self.price: float = 0.0
        self.client_rating = client_rating


class OwnerInterface:
    def __init__(self, taxi_park: "TaxiPark"):
        self.taxi_park = taxi_park

    def add_driver(self, driver: Driver):
        self.taxi_park.add_driver(driver)

    def add_car(self, car: Car):
        self.taxi_park.add_car(car)

    def get_financial_report(self) -> float:
        return self.taxi_park.calculate_total_earnings()


class DriverInterface:
    def __init__(self, taxi_park: "TaxiPark", driver_id: int):
        self.taxi_park = taxi_park
        self.driver_id = driver_id

    def accept_order(self, order_id: int) -> bool:
        return self.taxi_park.assign_driver_to_order(order_id)

    def complete_order(self, order_id: int):
        self.taxi_park.complete_order(order_id)

    def set_availability(self, available: bool):
        self.taxi_park.update_driver_availability(self.driver_id, available)


class TaxiPark(OrderSubject):
    def __init__(self):
        super().__init__()
        self.drivers: List[Driver] = []
        self.cars: List[Car] = []
        self.orders: Dict[int, Order] = {}
        self.pending_orders: List[Order] = []  # Очередь ожидающих заказов
        self.order_counter = 1

    def create_order(
        self, client_id: int, pickup: MapPoint, destination: MapPoint
    ) -> Order:
        order = Order(self.order_counter, client_id, pickup, destination)
        self.orders[order.order_id] = order
        self.order_counter += 1
        self.process_order(order)  # Пытаемся обработать заказ сразу
        return order

    def process_order(self, order: Order):
        available_drivers = self.get_available_drivers()
        if not available_drivers:
            self.pending_orders.append(order)  # Добавляем в очередь, если нет водителей
            return

        strategy = DriverAssignmentStrategy()
        selected_driver = strategy.select_driver(available_drivers, order)

        if selected_driver:
            self.assign_driver(order, selected_driver)
        else:
            self.pending_orders.append(order)

    def assign_driver(self, order: Order, driver: Driver):
        self.notify_drivers(order, driver.driver_id)
        order.status = "in_progress"
        order.driver = driver
        driver.current_order = order
        driver.is_available = False
        order.price = math.ceil(
            (
                (order.destination.x - order.pickup.x) ** 2
                + (order.destination.y - order.pickup.y) ** 2
            )
            ** 0.5
            * 0.5
        )

    def complete_order(self, order_id: int):
        order = self.orders.get(order_id)
        if order and order.status == "in_progress" and order.driver:
            order.status = "completed"
            driver = order.driver
            driver.is_available = True
            driver.current_order = None
            driver.set_location(order.destination.x, order.destination.y)

            # При освобождении водителя проверяем очередь заказов
            self.check_pending_orders()

    def check_pending_orders(self):
        if not self.pending_orders:
            return

        # Создаем копию, чтобы избежать проблем при изменении списка
        pending_copy = self.pending_orders.copy()
        self.pending_orders = []

        for order in pending_copy:
            if order.status == "pending":  # Проверяем, не был ли уже обработан
                self.process_order(order)

    def notify_drivers(self, order: Order, selected_driver_id: int):
        self.notify(order, selected_driver_id)

    def get_available_drivers(self) -> List[Driver]:
        return [driver for driver in self.drivers if driver.is_available]

    def add_driver(self, driver: Driver):
        self.drivers.append(driver)
        self.attach(driver)

    def get_rating(self, driver_id: int):
        if self.drivers[driver_id]:
            return self.drivers[driver_id].rating

    def change_driver_rating(self, driver_id: int, newRating: int):
        if self.drivers[driver_id]:
            self.drivers[driver_id].rating = max(
                min(
                    self.drivers[driver_id].rating
                    + (newRating - self.drivers[driver_id].rating) * 0.1,
                    5,
                ),
                0,
            )

    def add_car(self, car: Car):
        self.cars.append(car)

    def assign_driver_to_order(self, order_id: int) -> int:
        order = self.orders.get(order_id)
        if not order or order.status != "pending":
            return -1

        available_drivers = self.get_available_drivers()
        if not available_drivers:
            return -1

        strategy = DriverAssignmentStrategy()
        selected_driver = strategy.select_driver(available_drivers, order)

        if not selected_driver:
            return -1

        self.notify_drivers(order, selected_driver.driver_id)
        order.status = "in_progress"
        order.driver = selected_driver
        selected_driver.current_order = order
        selected_driver.is_available = False
        order.price = math.ceil(
            (
                (order.destination.x - order.pickup.x) ** 2
                + (order.destination.y - order.pickup.y) ** 2
            )
            ** 0.5
            * 0.5
        )

        return selected_driver.driver_id

    def get_order_status(self, order_id: int) -> str:
        return self.orders.get(order_id, Order(0, 0, "", "")).status

    def update_driver_availability(self, driver_id: int, available: bool):
        driver = next((d for d in self.drivers if d.driver_id == driver_id), None)
        if driver:
            driver.is_available = available

    def calculate_total_earnings(self) -> float:
        return sum(
            order.price for order in self.orders.values() if order.status == "completed"
        )


class ClientInterface:
    def __init__(self, taxi_park: "TaxiPark"):
        self.taxi_park = taxi_park

    def request_ride(
        self, client_id: int, pickup: MapPoint, destination: MapPoint
    ) -> Order:
        order = self.taxi_park.create_order(client_id, pickup, destination)
        driver_id = self.taxi_park.assign_driver_to_order(order.order_id)
        return order, driver_id

    def get_order_status(self, order_id: int) -> str:
        return self.taxi_park.get_order_status(order_id)
