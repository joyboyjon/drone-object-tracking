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
- `track_buffer`: 30 -> 60 (cate cadre este pastrat un obiect pierdut, aprox. 2 secunde)

### Concluzii

- Cu setarile implicite, aproximativ 86% din ID-uri erau pierdute: detectii aparute intr-un singur cadru porneau urmariri care erau sterse imediat.
- Pragul mai mare pentru urmariri noi a eliminat aproape toate aceste urmariri false (ID-urile pierdute au scazut de la aprox. 2190 la 80).
- Memoria mai lunga permite obiectelor acoperite pentru scurt timp sa isi pastreze ID-ul, in loc sa primeasca unul nou la revenire.

### Dezavantaje

- Persoanele foarte greu de vazut (mici, slab luminate), pentru care modelul nu ajunge niciodata la increderea 0.4, nu mai sunt urmarite deloc. O parte din scaderea numarului de ID-uri afisate (de la 366 la 196) vine din acest efect, nu doar din pastrarea mai buna a ID-urilor.
- Cele doua efecte nu pot fi separate exact, deoarece numarul real de persoane din clip nu este cunoscut.
- O memorie mai lunga creste riscul ca, la revenirea unui obiect pierdut, ID-ul sa fie atribuit gresit altei persoane aflate in apropiere.

Pentru proiect, compromisul este acceptabil: scopul este urmarirea stabila a unei singure tinte vizibile, nu detectarea tuturor persoanelor din imagine.