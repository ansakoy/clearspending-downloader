# clearspending-downloader
Download selected contract data from Clearspending.ru API as CSV file

### �����������

optional arguments:

  -h, --help          show this help message and exit

  -o , --output       �������� ��������� ����� CSV

  -b , --begin        ������ ������� � ����� ��.��.����

  -e , --end          ����� ������� � ����� ��.��.����

  -i , --inn          ��� ���������

  -k , --kpp          ��� ���������

  -r , --region       ��� ������� ���������

  -p , --pricerange   �������� ��� ����������, ��������: 10000-50000

  -f , --fz           ��, ��������: 94, 44, 223

  -C, --contracts     ��������� ������ � ������� 1 ������ = 1 ��������

  -P, --products      ��������� ������ � ������� 1 ������ = 1 �������


### ������� ��������


������� � ���� ����� test.csv ��� ��������� ��������������� ���������������-����������� ��������� ��� (��� 7803032323) ������� � 01.01.2016 � ������� 1 ������ - 1 ��������

`python contract_surfer.py -o test -i 7803032323 -b 01.01.2016 -C`

������, ������� ���������� �������� �� ������ ������� � 10.03.2017 � �� ���������� �������

`python contract_surfer.py -r 77 -b 10.03.2017`

������ ������� �������� ���������� ������������� ����������� ��� (��� 7830002078) �� ������ � 01.01.2015 �� 01.07.2016

`python contract_surfer.py -i 7830002078 -b 01.01.2015 -e 01.07.2016`

������ ������� �������� ���������� ��� ��� "����������� ���������" (��� 7840379186) �� ������ � 01.01.2011 �� ���������� �������

`python contract_surfer.py -i 7840379186 -b 01.01.2011`

������, ������� ���������� ���� ��������� �� ������ � 2016 �. �� 223-��

`python contract_surfer.py -r 77 -b 01.01.2016 -e 31.12.2016 -f 223`

������, ������� ���������� ���� ��������� �� ��� � 2016 �. �� 44-�� � ������� ��������� �� 100000 �� 1000000 ������

`python contract_surfer.py -r 78 -b 01.01.2016 -e 31.12.2016 -f 44 -p 100000-1000000`

��������� ������ � �������� ������������� ����������� ��� (��� 7830002078) �� ������ � 01.01.2016 �� ��������� ������ � ������� 1 ������ - 1 ������� � ��������� �� � ���� spb_gub_adm_2016-2017.csv

`python contract_surfer.py -o spb_gub_adm_2016-2017 -i 7830002078 -b 01.01.2016 -P`
