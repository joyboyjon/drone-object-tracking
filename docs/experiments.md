# Experimente

## Alegerea modelului YOLO si a rezolutiei de analiza

**Data:** 8 noiembrie 2026
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