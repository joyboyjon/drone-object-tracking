# Experimente

## Alegerea modelului YOLO si a rezolutiei de analiza

**Clip de test:** intersectie din Shinjuku, Tokyo, filmata de sus, noaptea (1280x606, 30 FPS, 628 de cadre)
**Hardware:** AMD Ryzen 7 5825U, 16 GB RAM, fara placa video dedicata (rulare pe procesor)

| Model   | imgsz | Persoane/cadru | Masini/cadru | FPS mediu |
|---------|------:|---------------:|-------------:|----------:|
| yolo11n |   640 |            3,4 |          5,4 |      26,4 |
| yolo11n |  1280 |           19,4 |          8,9 |      12,4 |
| yolo11s |   640 |            7,3 |          5,5 |      16,9 |
| yolo11s |   960 |           21,7 |          6,1 |       9,2 |
| yolo11s |  1280 |           31,7 |          9,0 |       5,6 |
| yolo11m |   640 |           12,8 |          8,7 |       7,7 |

### Concluzii

- Rezolutia de analiza conteaza mai mult decat marimea modelului: la 640 px, persoanele mici devin prea mici ca sa fie recunoscute.
- Modelul `m` la 640 este si mai lent, si mai slab decat `n` la 1280.
- Am ales **yolo11n cu imgsz=1280**: este singura configuratie cu detectie buna care depaseste pragul de 10 FPS si lasa rezerva de viteza pentru tracking, drona virtuala si comunicatie.
- Decizia va fi reevaluata dupa implementarea dronei virtuale, unde obiectele vor aparea mai mari in imagine.

### Observatii

- Valorile reprezinta obiectele detectate de model, nu numarul real de obiecte din clip.
- Modelul `n` confunda uneori masinile indepartate cu motociclete.

## Reglarea trackerului ByteTrack

**Clip de test:** acelasi clip din Shinjuku (1280x606, 30 FPS, 628 de cadre)
**Configuratie detectie:** yolo11n, imgsz=1280, clase urmarite: persoana si masina

Am masurat cate ID-uri diferite apar pe ecran si care este cel mai mare ID atribuit de tracker. Diferenta dintre cele doua arata cate urmariri au fost pornite, dar nu s-au confirmat niciodata (ID-uri "pierdute").

| Configuratie                            | ID-uri afisate | ID maxim |
|-----------------------------------------|---------------:|---------:|
| implicita (buffer 30, new_track 0.25)   |            366 |     2557 |
| modificata (buffer 60, new_track 0.4)   |            196 |      276 |

Parametri modificati in `config/bytetrack_custom.yaml`:

- `new_track_thresh`: 0.25 -> 0.4 (increderea minima pentru a porni o urmarire noua)
- `track_buffer`: 30 -> 60 (cate cadre este pastrat un obiect pierdut, aprox. 6 secunde)

### Concluzii

- Cu setarile implicite, aproximativ 86% din ID-uri erau pierdute: detectii aparute intr-un singur cadru porneau urmariri care erau sterse imediat.
- Pragul mai mare pentru urmariri noi a eliminat aproape toate aceste urmariri false (ID-urile pierdute au scazut de la aprox. 2190 la 80).
- Memoria mai lunga permite obiectelor acoperite pentru scurt timp sa isi pastreze ID-ul, in loc sa primeasca unul nou la revenire.

### Dezavantaje

- Persoanele foarte greu de vazut (mici, slab luminate), pentru care modelul nu ajunge niciodata la increderea 0.4, nu mai sunt urmarite deloc. O parte din scaderea numarului de ID-uri afisate (de la 366 la 196) vine din acest efect, nu doar din pastrarea mai buna a ID-urilor.
- Cele doua efecte nu pot fi separate exact, deoarece numarul real de persoane din clip nu este cunoscut.
- O memorie mai lunga creste riscul ca, la revenirea unui obiect pierdut, ID-ul sa fie atribuit gresit altei persoane aflate in apropiere.

Pentru proiect, compromisul este acceptabil: scopul este urmarirea stabila a unei singure tinte vizibile, nu detectarea tuturor persoanelor din imagine.

## Comparatie YOLO11 si YOLO26

Aceeasi metoda de masurare ca la primul experiment, pe acelasi clip. Toate rularile din acest tabel au fost facute dupa actualizarea bibliotecii Ultralytics (necesara pentru YOLO26).

| Model   | imgsz | Persoane/cadru | Masini/cadru | FPS mediu |
|---------|------:|---------------:|-------------:|----------:|
| yolo11n |  1280 |           18,5 |          8,5 |      12,5 |
| yolo26n |   640 |            1,7 |          3,5 |      23,3 |
| yolo26n |   960 |            6,9 |          7,3 |      18,1 |
| yolo26n |  1280 |           16,2 |          7,8 |      12,3 |
| yolo26s |  1280 |           30,1 |         12,4 |       5,4 |

### Concluzii

- YOLO26 este mai nou (lansat in ianuarie 2026), iar producatorul il prezinta ca fiind mai rapid pe procesor si mai bun la obiecte mici. Pe clipul si pe laptopul folosite aici, aceste avantaje nu s-au confirmat.
- La varianta nano si rezolutia 1280, YOLO11 detecteaza putin mai multe persoane si masini decat YOLO26, la aceeasi viteza.
- Variantele "s" ale ambelor familii au detectie foarte buna, dar sunt prea lente (sub 6 FPS) pentru urmarirea in timp real.
- Raman la **yolo11n cu imgsz=1280**.

### Observatii

- Masuratorile producatorului au fost facute cu modelul exportat in format ONNX, pe alt hardware. Aici modelul ruleaza direct in PyTorch, pe un procesor AMD fara placa video dedicata.
- Clipul de test (noapte, persoane foarte mici) este un caz particular; rezultatele pot fi diferite pe alte tipuri de imagini, de exemplu pe filmari aeriene de zi.
- Numarul de detectii depinde de pragul de incredere folosit (implicit 0.25). Daca un model da in general scoruri de incredere mai mici, pierde mai multe detectii la acelasi prag.
- Reluarea testului cu yolo11n dupa actualizarea bibliotecii a dat valori cu cateva procente diferite fata de prima masurare (18,5 fata de 19,4 persoane/cadru). Diferentele mici dintre configuratii nu trebuie deci considerate semnificative.

## Alegerea automata a tintei (tip + marime)

Configuratie: tinta = persoana, regula = cea mai mare, asteptare = 60 de cadre.

| Indicator                 | Valoare    |
|---------------------------|-----------:|
| Cadre procesate           |        628 |
| Tinte alese               |          3 |
| Cadre cu tinta vizibila   | 417 (66%)  |

Evolutia increderii modelului pentru fiecare tinta, la alegere si in momentele in care a fost pierduta:

| Tinta | Increderea                                    |
|-------|-----------------------------------------------|
| 11    | 0.44 (alegere) -> 0.50 -> 0.28 -> 0.11        |
| 63    | 0.36 (alegere) -> 0.51 -> 0.27 -> 0.24 -> 0.10 |
| 146   | 0.65 (alegere) -> 0.32 -> 0.25 -> 0.14 -> 0.13 |

### Observatii

- Tinta isi pastreaza ID-ul dupa pierderi scurte (pana la 34 de cadre in test), datorita memoriei trackerului.
- Regula "cea mai mare" alege persoane din partea de jos a imaginii, deoarece acestea sunt cele mai apropiate de camera.
- Tinta este pierduta intermitent chiar daca persoana este vizibila integral in imagine. In 7 din 9 pierderi, increderea modelului scazuse treptat sub pragurile trackerului (ultimele valori: 0.10-0.32).
- Increderea scade pe masura ce persoana se apropie de coltul din stanga-jos. Cauza probabila: camera este montata sus, iar persoanele apropiate sunt vazute aproape de deasupra, diferit de imaginile pe care a fost antrenat modelul.
- In 2 din 9 pierderi tinta a disparut brusc, cu incredere buna (0.50-0.51). Cauza probabila este alta (de exemplu apropierea de alte persoane).
- Aceeasi persoana a primit doua ID-uri diferite (11 si 63): dupa 60 de cadre fara detectie, trackerul a renuntat la ID-ul vechi, iar la redetectare persoana a fost considerata un obiect nou. ByteTrack nu compara aspectul obiectelor, ci doar pozitia si marimea lor.

### Imbunatatiri planificate (M3)

- Regasirea tintei dupa pozitie, marime si culoare, pentru a recunoaste aceeasi persoana chiar daca trackerul i-a atribuit un ID nou.
- Evitarea alegerii tintelor aflate la marginea imaginii.
- Optional: testarea unui prag minim de incredere mai mic pentru tracker.

## Alegerea tintei prin click si analiza miscarii

### Alegerea prin click

| Mod de alegere        | Tinte alese | Cadre cu tinta vizibila |
|-----------------------|------------:|------------------------:|
| automat (cea mai mare)|           3 |               417 (66%) |
| manual (click)        |          11 |               504 (80%) |

- Prin click au fost alese persoane usor de vazut, cu incredere mare (0.86, 0.69, 0.61), in timp ce alegerea automata lua persoanele cele mai mari din partea de jos a imaginii, detectate mai slab.
- Un click poate rata daca persoana nu este detectata exact in acel moment (detectie intermitenta). Al doilea click, in acelasi loc, a selectat persoana corect.
- O persoana mica, aflata departe de camera (tinta 197, arie 364 px), a fost urmarita 151 de cadre fara nicio pierdere, in timp ce persoanele mari din partea de jos se pierdeau la fiecare 7-8 cadre. Acest lucru sustine ipoteza ca unghiul de sus afecteaza detectia persoanelor apropiate de camera.

### Analiza miscarii

- Viteza se calculeaza din pozitiile centrului tintei, in pixeli pe secunda, folosind numarul de cadre al clipului (30 FPS), nu viteza de procesare.
- Cu o fereastra de 10 pozitii, sageata de directie avea mici variatii de scurta durata, cauzate de modificarile chenarului (pozitia picioarelor, incredere mica). Cu 20 de pozitii, sageata este mai stabila, dar reactioneaza mai lent la schimbarile de directie. Am ales 20.
- Traseul este pastrat pentru fiecare obiect ales cel putin o data, inclusiv in perioadele in care nu este tinta curenta. La revenirea la o tinta anterioara, traseul este afisat complet.
- Limita: daca trackerul atribuie un ID nou aceleiasi persoane, istoricul porneste de la zero.

### Imbunatatiri planificate (M5)

- Incredere minima pentru alegerea automata a tintei (de exemplu 0.4), pentru a evita tintele detectate slab.