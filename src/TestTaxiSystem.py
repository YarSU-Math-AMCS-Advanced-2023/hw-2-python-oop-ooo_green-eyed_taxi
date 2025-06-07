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
        order = self.client.request_ride(101, start, end)
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

    # def test_order_creation_and_notification(self):
    #     print("\n--- Тест 1: Создание заказа и уведомление водителей ---")
    #     print("Клиент создает заказ из 'ул. Союзная д.141' в 'ул. Союзная д.144'")
    #     order = self.client.request_ride(101, "ул. Союзная д.141", "ул. Союзная д.144")

    #     print(f"Создан заказ #{order.order_id}:")
    #     print(f"  Откуда: {order.pickup}")
    #     print(f"  Куда: {order.destination}")
    #     print(f"  Статус: {order.status}")

    #     self.assertEqual(order.status, "pending")
    #     print("✅ Статус заказа корректно установлен как 'pending'")

    #     status = self.client.get_order_status(order.order_id)
    #     print(f"Проверка статуса через клиента: {status}")
    #     self.assertEqual(status, "pending")
    #     print("✅ Клиентская часть верно отображает статус заказа")

    # def test_driver_acceptance_process(self):
    #     print("\n--- Тест 2: Процесс принятия заказа водителем ---")
    #     print("Клиент создает заказ из 'Красная площадь' в 'Московский вокзал'")
    #     order = self.client.request_ride(102, "Красная площадь", "Московский вокзал")

    #     print("\nПроверка доступности водителей:")
    #     print(
    #         f"  {self.driver1.name}: {'доступен' if self.driver1.is_available else 'не доступен'}"
    #     )
    #     print(
    #         f"  {self.driver2.name}: {'доступен' if self.driver2.is_available else 'не доступен'}"
    #     )

    #     driver_id = self.taxi_park.assign_driver_to_order(order.order_id)
    #     print(f"✅ Заказ #{order.order_id} успешно принят водителем {driver_id}")

    #     print(f"\nОбновленный статус заказа: {order.status}")
    #     self.assertEqual(order.status, "in_progress")
    #     print("✅ Статус заказа корректно обновлен на 'in_progress'")

    #     # print(f"\nСостояние водителя {self.driver1.name}:")
    #     # print(
    #     #     f"  Доступность: {'доступен' if self.driver1.is_available else 'не доступен'}"
    #     # )
    #     # print(
    #     #     f"  Текущий заказ: #{self.driver1.current_order.order_id if self.driver1.current_order else 'нет'}"
    #     # )
    #     # self.assertFalse(self.driver1.is_available)
    #     # self.assertEqual(self.driver1.current_order.order_id, order.order_id)
    #     # print("✅ Состояние водителя корректно обновлено")

    # def test_order_lifecycle(self):
    #     print("\n--- Тест 3: Полный цикл заказа ---")
    #     print("Клиент создает заказ из 'Московский вокзал' в 'ул. Клубная д.62'")
    #     order = self.client.request_ride(103, "Московский вокзал", "ул. Клубная д.62")

    #     print("\nВодитель 2 принимает заказ")
    #     self.driver_interface2.accept_order(order.order_id)
    #     print(f"Текущий водитель заказа: {order.driver.name}")
    #     print(f"Статус заказа: {order.status}")

    #     print("\nВодитель 2 завершает заказ")
    #     self.driver_interface2.complete_order(order.order_id)

    #     print(f"\nИтоговый статус заказа: {order.status}")
    #     self.assertEqual(order.status, "completed")
    #     print("✅ Статус заказа корректно обновлен на 'completed'")

    #     print(f"\nСостояние водителя {self.driver2.name}:")
    #     print(
    #         f"  Доступность: {'доступен' if self.driver2.is_available else 'не доступен'}"
    #     )
    #     print(f"  Текущий заказ: {'есть' if self.driver2.current_order else 'нет'}")
    #     self.assertTrue(self.driver2.is_available)
    #     self.assertIsNone(self.driver2.current_order)
    #     print("✅ Состояние водителя корректно обновлено после завершения поездки")

    #     print(f"\nСтоимость поездки: {order.price} руб.")
    #     self.assertEqual(order.price, 10.0)
    #     print("✅ Стоимость поездки рассчитана")

    # def test_financial_reporting(self):
    #     print("\n--- Тест 4: Финансовая отчетность ---")
    #     print("Создаем и выполняем 2 заказа")

    #     print("\nЗаказ 1: 'Парк Горького' -> 'ВДНХ'")
    #     order1 = self.client.request_ride(104, "Парк Горького", "ВДНХ")
    #     self.driver_interface1.accept_order(order1.order_id)
    #     self.driver_interface1.complete_order(order1.order_id)
    #     print(f"Завершен заказ #{order1.order_id}, стоимость: {order1.price} руб.")

    #     print("\nЗаказ 2: 'Арбат' -> 'Храм Христа Спасителя'")
    #     order2 = self.client.request_ride(105, "Арбат", "Храм Христа Спасителя")
    #     self.driver_interface2.accept_order(order2.order_id)
    #     self.driver_interface2.complete_order(order2.order_id)
    #     print(f"Завершен заказ #{order2.order_id}, стоимость: {order2.price} руб.")

    #     total_earnings = self.owner.get_financial_report()
    #     print(f"\nОбщая выручка таксопарка: {total_earnings} руб.")
    #     self.assertEqual(total_earnings, 20.0)
    #     print("✅ Общая выручка рассчитана корректно")

    # def test_driver_availability_management(self):
    #     print("\n--- Тест 5: Управление доступностью водителей ---")
    #     print("Устанавливаем водителю 1 статус 'недоступен'")
    #     self.driver_interface1.set_availability(False)
    #     print(
    #         f"Состояние водителя {self.driver1.name}: {'доступен' if self.driver1.is_available else 'недоступен'}"
    #     )

    #     print("\nКлиент создает новый заказ")
    #     order = self.client.request_ride(
    #         106, "проспект Ленина д.61", "ул. 30 лет Октября д.1"
    #     )

    #     print("\nПопытка принять заказ недоступным водителем")
    #     driver_id = self.driver_interface1.accept_order(order.order_id)
    #     success = driver_id == -1
    #     self.assertFalse(success)
    #     print("✅ Недоступный водитель не смог принять заказ")

    #     print("\nВозвращаем доступность водителя")
    #     self.driver_interface1.set_availability(True)
    #     print(
    #         f"Состояние водителя {self.driver1.name}: {'доступен' if self.driver1.is_available else 'недоступен'}"
    #     )

    #     print("\nПопытка принять заказ снова")
    #     driver_id = self.driver_interface1.accept_order(order.order_id)
    #     success = driver_id != -1
    #     self.assertFalse(success)
    #     print("✅ Теперь водитель успешно принял заказ")

    # def test_multiple_orders_processing(self):
    #     print("\n--- Тест 6: Обработка нескольких заказов одновременно ---")
    #     print("Создаем 3 заказа одновременно")

    #     order1 = self.client.request_ride(
    #         107, "Третьяковская галерея", "Новодевичий монастырь"
    #     )
    #     order2 = self.client.request_ride(108, "Старый Арбат", "Поклонная гора")
    #     order3 = self.client.request_ride(109, "Кремль", "Храм Василия Блаженного")

    #     print("\nВодители принимают заказы:")
    #     print(f"Водитель 1 принимает заказ #{order1.order_id}")
    #     self.driver_interface1.accept_order(order1.order_id)

    #     print(f"Водитель 2 принимает заказ #{order2.order_id}")
    #     self.driver_interface2.accept_order(order2.order_id)

    #     print("\nПопытка принять третий заказ (нет свободных водителей)")
    #     driver_id = self.driver_interface1.accept_order(order3.order_id)
    #     success = driver_id != -1
    #     self.assertFalse(success)
    #     print("✅ Третий заказ не может быть принят (нет свободных водителей)")

    #     print("\nЗавершаем первый заказ")
    #     self.driver_interface1.complete_order(order1.order_id)

    #     print("Теперь пробуем принять третий заказ")
    #     driver_id = self.driver_interface1.accept_order(order3.order_id)
    #     success = driver_id == -1
    #     self.assertFalse(success)
    #     print("✅ Третий заказ успешно принят после освобождения водителя")


if __name__ == "__main__":
    print("================ ЗАПУСК ТЕСТИРОВАНИЯ ================")
    unittest.main(verbosity=2)
    print("================ КОНЕЦ ================")
