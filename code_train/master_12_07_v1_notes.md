# master_12_07_v1

Nguon phan tich:

- Nhom version gan nhat 09/07 co val macro F1 tot nhat, vuot moc 0.91 va on dinh hon cac ban truoc.
- Ban 26/06 co xu huong overfit ro: train F1 tang nhanh nhung val F1 plateau.
- Cau hinh co hieu qua nhat la PhoBERT + LLRD + cosine schedule + dropout cao hon, nhung can them xu ly mat can bang cho lop hien.

Diem toi uu trong version moi:

- Dung `labeled_results_all_v2.json` theo yeu cau nguon du lieu.
- Stratified split theo to hop 4 nhan de giu phan bo gan voi tap goc hon.
- WeightedRandomSampler de uu tien mau co nhan hiem.
- Mo hinh fusion CLS + mean pooling, giup on dinh hon chi dung CLS.
- Head rieng cho tung aspect, co multisample dropout.
- Loss co class weight va label smoothing, trong do Atmosphere va Food quality duoc scale cao hon nhe.
- Chon checkpoint theo score can bang giua macro F1 va recall te nhat de giam sai so trong confusion matrix.

File chay chinh:

- `master_12_07_v1.py`

File phu tro khi train:

- `best_phobert_absa_v12.pth`
- `master_12_07_v1_report.json`
- `master_12_07_v1_confusion.png`
