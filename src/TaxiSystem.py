from abc import ABC, abstractmethod
from typing import List, Optional, Dict


class OrderSubject:
    def __init__(self):
        self._observers: List[Driver] = []

    def attach(self, observer: "Driver"):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: "Driver"):
        self._observers.remove(observer)

    def notify(self, order: "Order"):
        for observer in self._observers:
            if observer.is_available:
                observer.update(order)


class Driver:
    def __init__(self, driver_id: int, name: str):
        self.driver_id = driver_id
        self.name = name
        self.is_available = True
        self.current_order: Optional["Order"] = None

    def update(self, order: "Order"):
        if self.is_available:
            print(f"Водитель {self.name} получил уведомление о заказе {order.order_id}")


class Car:
    def __init__(self, car_id: int, model: str, license_plate: str):
        self.car_id = car_id
        self.model = model
        self.license_plate = license_plate
        self.is_available = True


class Order:
    def __init__(self, order_id: int, client_id: int, pickup: str, destination: str):
        self.order_id = order_id
        self.client_id = client_id
        self.pickup = pickup
        self.destination = destination
        self.status = "pending"  # pending, in_progress, completed
        self.driver: Optional[Driver] = None
        self.price: float = 0.0


class ClientInterface:
    def __init__(self, taxi_park: "TaxiPark"):
        self.taxi_park = taxi_park

    def request_ride(self, client_id: int, pickup: str, destination: str) -> Order:
        order = self.taxi_park.create_order(client_id, pickup, destination)
        self.taxi_park.notify_drivers(order)
        return order

    def get_order_status(self, order_id: int) -> str:
        return self.taxi_park.get_order_status(order_id)


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
        return self.taxi_park.assign_driver_to_order(order_id, self.driver_id)

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
        self.order_counter = 1

    def create_order(self, client_id: int, pickup: str, destination: str) -> Order:
        order = Order(self.order_counter, client_id, pickup, destination)
        self.orders[order.order_id] = order
        self.order_counter += 1
        return order

    def notify_drivers(self, order: Order):
        self.notify(order)

    def add_driver(self, driver: Driver):
        self.drivers.append(driver)
        self.attach(driver)

    def add_car(self, car: Car):
        self.cars.append(car)

    def assign_driver_to_order(self, order_id: int, driver_id: int) -> bool:
        order = self.orders.get(order_id)
        driver = next((d for d in self.drivers if d.driver_id == driver_id), None)

        if order and driver and driver.is_available and order.status == "pending":
            order.status = "in_progress"
            order.driver = driver
            driver.current_order = order
            driver.is_available = False
            order.price = 10.0
            return True
        return False

    def complete_order(self, order_id: int):
        order = self.orders.get(order_id)
        if order and order.status == "in_progress" and order.driver:
            order.status = "completed"
            order.driver.is_available = True
            order.driver.current_order = None

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
