import unittest
import json
from TaxiSystem import (
    TaxiPark,
    Driver,
    Car,
    MapPoint,
    ClientInterface,
    OwnerInterface,
    DriverInterface,
)


class TestTaxiSystem(unittest.TestCase):
    def setUp(self):
        print("\n\n=== Тестовые данные ===")
        self.taxi_park = TaxiPark()
        self.owner = OwnerInterface(self.taxi_park)

        with open("tests/drivers.json", "r", encoding="utf-8") as f:
            drivers_data = json.load(f)
            self.drivers = [
                Driver(driver["driver_id"], driver["name"]) for driver in drivers_data
            ]

        with open("tests/addresses.json", "r", encoding="utf-8") as f:
            addresses_data = json.load(f)
            self.addresses = [
                MapPoint(address["id"], address["name"], address["x"], address["y"])
                for address in addresses_data
            ]

        with open("tests/cars.json", "r", encoding="utf-8") as f:
            cars_data = json.load(f)
            self.cars = [
                Car(car["car_id"], car["model"], car["license_plate"])
                for car in cars_data
            ]

        print("Добавляем водителей и автомобили:")
        for driver in self.drivers:
            self.owner.add_driver(driver)
        for car in self.cars:
            self.owner.add_car(car)

        driver_names = ", ".join([driver.name for driver in self.drivers])
        car_models = ", ".join([car.model for car in self.cars])
        print(f"Добавлены водители: {driver_names}")
        print(f"Добавлены автомобили: {car_models}")

        self.client = ClientInterface(self.taxi_park)
        self.driver_interfaces = [
            DriverInterface(self.taxi_park, driver.driver_id) for driver in self.drivers
        ]
        print("=== Тестовые данные готовы ===\n")

    def get_address(self, address_id):
        """Получение адреса по ID"""
        for address in self.addresses:
            if address.id == address_id:
                return address

    def test_order_creation(self):
        print("\n--- Тест 1: Создание заказа и уведомление водителя ---")
        start = self.get_address(1)
        end = self.get_address(3)
        print(f"Клиент создает заказ из {start.name} в {end.name}")
        order, driver_id = self.client.request_ride(101, start, end)
        print(f"Создан заказ #{order.order_id}:")
        print(f"  Откуда: {order.pickup.name}")
        print(f"  Куда: {order.destination.name}")
        print(f"  Статус: {order.status}")
        self.assertEqual(order.status, "in_progress")
        print("✅ Статус заказа корректно установлен как 'in_progress'")
        status = self.client.get_order_status(order.order_id)
        print(f"Проверка статуса через клиента: {status}")
        self.assertEqual(status, "in_progress")
        print("✅ Клиентская часть верно отображает статус заказа")

    def test_the_end_of_order(self):
        print("\n--- Тест 2: Окончание поездки ---")
        start = self.get_address(2)
        end = self.get_address(4)
        print(f"Клиент создает заказ из {start.name} в {end.name}")
        order, driver_id = self.client.request_ride(101, start, end)
        status = self.client.get_order_status(order.order_id)
        print(f"Проверка статуса через клиента: {status}")
        self.assertEqual(status, "in_progress")
        print("✅ Клиентская часть верно отображает статус заказа")
        self.driver_interfaces[order.driver.driver_id].complete_order(order.order_id)
        self.assertEqual(order.status, "completed")
        print("✅ Статус заказа корректно установлен как 'completed'")

    def test_two_clients_the_same_time(self):
        print("\n--- Тест 3: одновременный жизненный цикл двойного заказа ---")
        start1 = self.get_address(2)
        end1 = self.get_address(4)

        start2 = self.get_address(4)
        end2 = self.get_address(2)

        print(f"Клиент создает заказ из {start1.name} в {end1.name}")
        order1, driver_id = self.client.request_ride(101, start1, end1)

        print(f"Клиент создает заказ из {start2.name} в {end2.name}")
        order2, driver_id = self.client.request_ride(111, start2, end2)

        status1 = self.client.get_order_status(order1.order_id)
        status2 = self.client.get_order_status(order2.order_id)

        print(f"Проверка статуса через клиента: {status1}")
        self.assertEqual(status1, "in_progress")
        print(f"Проверка статуса через клиента: {status2}")
        self.assertEqual(status2, "in_progress")
        print("✅ Клиентская часть верно отображает статус заказа")

        self.driver_interfaces[order1.driver.driver_id].complete_order(order1.order_id)
        self.assertEqual(order1.status, "completed")
        print("✅ Статус 1-го заказа корректно установлен как 'completed'")

        self.driver_interfaces[order2.driver.driver_id].complete_order(order2.order_id)
        self.assertEqual(order2.status, "completed")
        print("✅ Статус 2-го заказа корректно установлен как 'completed'")

    def test_dearth_drivers(self):
        print("\n--- Тест 4: Нехватка водителей ---")
        start1 = self.get_address(2)
        end1 = self.get_address(4)

        start2 = self.get_address(4)
        end2 = self.get_address(2)

        start3 = self.get_address(1)
        end3 = self.get_address(5)

        print(f"Клиент создает заказ из {start1.name} в {end1.name}")
        order1, driver_id = self.client.request_ride(101, start1, end1)

        print(f"Клиент создает заказ из {start2.name} в {end2.name}")
        order2, driver_id = self.client.request_ride(111, start2, end2)

        print(f"Клиент создает заказ из {start3.name} в {end3.name}")
        order3, driver_id = self.client.request_ride(121, start3, end3)
        if driver_id == -1:
            print("Свободных водителей пока нет. Ожидайте...")

        self.driver_interfaces[order1.driver.driver_id].complete_order(order1.order_id)
        print(self.client.get_order_status(order3.order_id))

    def test_financial_reporting(self):
        print("\n--- Тест 5: Финансовая отчетность ---")
        print("Создаем и выполняем 2 заказа")

        start1 = self.get_address(2)
        end1 = self.get_address(4)

        start2 = self.get_address(6)
        end2 = self.get_address(2)

        print(f"Клиент создает заказ из {start1.name} в {end1.name}")
        order1, driver_id = self.client.request_ride(101, start1, end1)
        print(f"Стоимость заказа: {order1.price} руб.")

        print(f"Клиент создает заказ из {start2.name} в {end2.name}")
        order2, driver_id = self.client.request_ride(111, start2, end2)
        print(f"Стоимость заказа: {order2.price} руб.")

        self.driver_interfaces[order1.driver.driver_id].complete_order(order1.order_id)
        self.driver_interfaces[order2.driver.driver_id].complete_order(order2.order_id)

        total_earnings = self.owner.get_financial_report()
        print(f"\nОбщая выручка таксопарка: {total_earnings} руб.")
        self.assertEqual(total_earnings, order1.price + order2.price)
        print("✅ Общая выручка рассчитана корректно")

    def test_rating_drivers(self):
        print("\n--- Тест 6: Рейтинг водителей ---")
        start1 = self.get_address(2)
        end1 = self.get_address(4)

        print(f"Клиент создает заказ из {start1.name} в {end1.name}")
        order1, driver_id = self.client.request_ride(101, start1, end1)

        self.driver_interfaces[order1.driver.driver_id].complete_order(order1.order_id)
        print("Заказ завершён")
        self.taxi_park.change_driver_rating(driver_id, 4)
        print(f"Новый рейтинг равен {self.taxi_park.get_rating(driver_id)}")


if __name__ == "__main__":
    print("================ ЗАПУСК ТЕСТИРОВАНИЯ ================")
    unittest.main(verbosity=2)
    print("================ КОНЕЦ ================")
