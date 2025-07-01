from datasets import load_dataset, Dataset, DatasetDict
import random
import calendar

class CareerGenerator:

    def __init__(self):
        dataset = load_dataset("jensjorisdecorte/anonymous-working-histories")
        self.train_data = dataset["train"] # 1720 records
        self.test_data = dataset["test"]   # 227 records

    def __get_month_name(self, month_number):
        month_number = int(month_number)
        if 1 <= month_number <= 12:
            return calendar.month_name[month_number]
        else:
            return None

    def __get_season(self, month_number):
        month_number = int(month_number)
        if 1 <= month_number <= 12:
            if month_number in (12, 1, 2):
                return "Winter"
            elif month_number in (3, 4, 5):
                return "Spring"
            elif month_number in (6, 7, 8):
                return "Summer"
            elif month_number in (9, 10, 11):
                return "Autumn"
        else:
            return None

    def __fix_date(self, raw_date):
        substrings = raw_date.split("/")
        if len(substrings) == 2:

            if random.choice([1, 2]) == 1:
                month_season = self.__get_month_name(substrings[0])
            else:
                month_season = self.__get_season(substrings[0])

            if month_season != None:
                return month_season + " " + substrings[1]
            else:
                return raw_date
        else:
            return raw_date        

    def generate_career(self, record=None, dataset="train"):
        if record is None:
            random_number = random.randint(0, len(self.train_data))
            number = random_number
        else:
            number = record

        if dataset == "train":
            row = self.train_data[number]
        else:
            row = self.test_data[number]

        career = """"""
        ann_help_list = []  

        for idx in range(17):
            if row[f"title_{idx}"] != None:
                sublist = []
                title = row[f"title_{idx}"]
                sublist.append(title)
                description = row[f"description_{idx}"]
                start_raw = row[f"start_{idx}"]
                start = self.__fix_date(start_raw)
                sublist.append(start)
                end_raw = row[f"end_{idx}"]
                if end_raw == "current":
                    end = "this day"
                    sublist.append("current job")
                else:
                    end = self.__fix_date(end_raw)
                    sublist.append(end)

                if idx == 0:
                    career += f"First role: {title} from {start} to {end}.\nExperiences:"
                else:
                    career += f"\n\nNext role: {title} from {start} to {end}.\nExperiences:"
        
                career += f"\n{description}"
                ann_help_list.append(sublist)
            
            if idx == 2:
                break

        return career, number

    def generate_local_dataset(self):

        career_list = []
        ann_help_list_list = []

        for idx in range(3):
            career, ann_help_list = self.generate_career(idx, "train")
            career_list.append(career)
            ann_help_list_list.append(ann_help_list)
        
        train_data = {
        'career': career_list,
        'ann_help_list': ann_help_list_list
        }

        train_dataset = Dataset.from_dict(train_data)
        train_dataset.to_csv("my_train_data.csv")

        dataset = load_dataset('csv', data_files={
        'train': 'train_data.csv',
        })

        train_dataset = dataset["train"]
        print(train_dataset[0]["career"])
        print(train_dataset[0]["ann_help_list"])

def main():
    import sys
    if len(sys.argv) > 1:
        record = int(sys.argv[1])
    else:
        record = None

    cg = CareerGenerator()

    career, number = cg.generate_career(record)

    print(number)
    print(career)

if __name__ == '__main__':
    main()

