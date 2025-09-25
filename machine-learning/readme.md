# Refs
- Sách miễn phí “Neural Networks and Deep Learning” (Michael Nielsen): https://notebooklm.google.com/notebook/d9c578e6-55dc-43bd-bb50-28ac41628a7c
- Series video 3Blue1Brown “What is a neural network?”: https://www.youtube.com/watch?v=aircAruvnKk&list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi
- Blog của Chris Olah (colah): https://colah.github.io/
- Deep Learning Specialization (Andrew Ng): https://www.coursera.org/specializations/deep-learning
- Fast.ai: https://github.com/fastai/fastbook, https://docs.fast.ai/, https://fastpages.fast.ai/, https://forums.fast.ai/
- https://distill.pub/
- Kaggle – Mini-course về ML, DL, kèm dữ liệu thực hành.
- https://research.google/blog/
- https://github.com/airctic/icevision
- https://github.com/jsbroks/awesome-dataset-tools

## More Sepecification

### timm
- https://christianjmills.com/posts/pytorch-train-image-classifier-timm-hf-tutorial/

### fastai

---
# Reserch

## 🧩 1. Bản chất của segmentation với biên phức tạp
- **Mục tiêu**: không chỉ phân biệt foreground–background, mà còn phải **bám sát từng pixel** ở biên dạng phức tạp (tay, tóc, quần áo).  
- **Thách thức**:  
  - Biên thường mảnh, dễ bị mất khi downsampling trong CNN.  
  - Màu sắc foreground có thể trùng với background ở một số vùng.  
  - Object người có nhiều tư thế, hình dạng biến thiên mạnh.  

## 🧩 2. Các dòng kiến trúc chính
### 🔹 U-Net và biến thể
- **U-Net**: encoder–decoder + skip connections → giữ chi tiết biên.  
- **U-Net++**: skip connections dày đặc hơn → biên mượt hơn.  
- **Attention U-Net**: tập trung vào vùng có object, giảm nhiễu nền.  
- **Điểm ít ai để ý**: U-Net rất mạnh khi dữ liệu không quá lớn, nhưng dễ bị “quá khớp” nếu augmentation không đủ đa dạng.

### 🔹 DeepLab series
- **DeepLabv3+**: atrous convolution + decoder tinh chỉnh biên.  
- **Ưu điểm**: nắm bắt ngữ cảnh đa tỉ lệ, biên sắc nét hơn Mask R-CNN.  
- **Điểm ít ai để ý**: atrous conv giúp giữ resolution, nhưng nếu stride không khéo, có thể bỏ sót chi tiết nhỏ.

### 🔹 Mask R-CNN
- Instance segmentation, phân biệt từng người riêng biệt.  
- **Điểm yếu**: mask thường hơi “blocky” ở biên nhỏ, trừ khi dùng backbone rất mạnh.

### 🔹 Transformer-based
- **SegFormer**: nhẹ, chính xác, biên tốt nhờ attention đa tỉ lệ.  
- **Mask2Former**: SOTA, unify semantic/instance/panoptic segmentation.  
- **SAM (Segment Anything Model)**: biên cực chi tiết, nhưng cần fine-tune cho dữ liệu riêng.  
- **Điểm ít ai để ý**: attention map trong transformer có thể “nhìn xuyên” màu sắc, nên đôi khi phân biệt object ngay cả khi foreground–background gần giống nhau.

## 🧩 3. Vai trò của màu sắc
- **Có lợi**: nếu foreground (đen) và background sáng → mô hình dễ học.  
- **Hạn chế**: nếu nền cũng tối, màu sắc không còn phân biệt tốt → phải dựa vào biên hình học.  
- **Điểm ít ai để ý**: augmentation màu (brightness, contrast, hue) không chỉ để tăng dữ liệu, mà còn giúp mô hình **không phụ thuộc tuyệt đối vào màu đen** của object. Điều này quan trọng nếu sau này object không còn “đen tuyệt đối” nữa.

## 🧩 4. Kỹ thuật bổ trợ để biên chính xác hơn
- **Edge-aware loss**: thêm thành phần loss tập trung vào biên (Boundary Loss, Dice Loss kết hợp).  
- **Multi-task learning**: train segmentation + edge detection song song.  
- **Kênh bổ sung**: ngoài RGB, thêm kênh edge (Canny, Sobel) hoặc frequency (Fourier) để mô hình “nhìn” rõ biên.  
- **Test Time Augmentation (TTA)**: lật, xoay ảnh khi inference rồi ensemble → biên mượt hơn.  
- **Điểm ít ai để ý**: nhiều nhóm nghiên cứu dùng **CRF (Conditional Random Field)** hoặc **Graph-based refinement** sau segmentation để “làm sắc nét” biên, nhưng thường bị bỏ qua vì tốn thời gian.


## 🧩 5. Lựa chọn thực tế cho bài toán của bạn
- **Nếu dữ liệu vừa phải, muốn triển khai nhanh** → **U-Net++ hoặc Attention U-Net**.  
- **Nếu dữ liệu lớn, muốn SOTA, biên sắc nét** → **DeepLabv3+ hoặc SegFormer**.  
- **Nếu muốn đa năng, thử nghiệm nhanh, biên cực chi tiết** → **SAM hoặc Mask2Former** (nhưng cần GPU mạnh).  
- **Nếu cực kỳ quan tâm đến biên** → kết hợp segmentation backbone + edge-aware loss + CRF refinement.  


## 🧩 6. Kết luận chiến lược
- **Màu sắc**: hữu ích nhưng không đủ → phải kết hợp biên hình học.  
- **Kiến trúc**: chọn U-Net++/DeepLabv3+/SegFormer tuỳ dữ liệu và tài nguyên.  
- **Tinh chỉnh**: dùng loss chuyên cho biên + augmentation màu + edge channel.  
- **Điểm ít ai để ý**: nhiều mô hình đạt mIoU cao nhưng biên vẫn xấu; để tối ưu biên, cần **loss và post-processing chuyên biệt**, không chỉ backbone mạnh.


👉 Tóm gọn: Nếu bạn muốn **biên người đen trên nền sáng** thật chính xác, giải pháp tối ưu là **DeepLabv3+ hoặc SegFormer**, kết hợp **edge-aware loss** và **augmentation màu**, có thể thêm **CRF refinement** để “mài sắc” biên.  


## 🧠 Mô hình
- **DeepLabv3+**  
  - Mạnh về multi-scale context (ASPP) + decoder refine biên.  
  - Rất hợp cho bài toán cần **biên sắc nét**.  
- **SegFormer**  
  - Transformer-based, nhẹ hơn, generalize tốt, đặc biệt khi dữ liệu đa dạng ánh sáng/màu.  
  - Thường outperform trên dataset mới.

## 🔧 Kỹ thuật tăng cường
- **Edge-aware loss** (Boundary loss, Dice + BCE + Edge loss): ép model học biên tốt hơn.  
- **Color augmentation** (brightness/contrast jitter, hue shift): giúp model robust với nền sáng/tối.  
- **CRF refinement**: mài sắc biên, đặc biệt khi foreground–background tương phản mạnh.

## 📌 Gợi ý pipeline tối ưu
1. Dùng **mmsegmentation** với backbone từ **timm** (ví dụ Swin Transformer).  
2. Chạy **SegFormer** baseline → so sánh với **DeepLabv3+**.  
3. Thêm **edge-aware loss** (Boundary loss hoặc Sobel-based edge supervision).  
4. Áp dụng **color jitter + random gamma** augmentation.  
5. Hậu xử lý bằng **DenseCRF** hoặc **GraphCut refinement** để sharpen mask.  

