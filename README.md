## Outcome-Oriented Prescriptive Process Monitoring with Selectable Index Encoding

This repository implements a prescriptive process monitoring system that offers recommendations for achieving positive process outcomes. It leverages index encoding (simple or complex) to suggest specific activities and their optimal execution times.

**Project Inspiration**

This work builds upon the temporal prescriptive process monitoring system developed by ivanDonadello ([Ivan's project link](https://github.com/ivanDonadello/temporal-prescriptive-process-monitoring_old.git)). That system focuses on identifying temporal relationships between process activities to provide recommendations.

**Running the Experiments**

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/GoldenRose01/Thesis
   ```

2. **Set Up the Environment:**
   - **Verify Virtual Environment:** Check if a virtual environment named `.venv` exists. If not, install the required libraries listed in `requirements.txt`. You can use `pip install -r requirements.txt` to install them.
   - **Create a `.env` File:** In the project's root directory, create a file named `.env`. Add a line specifying the path to the `Graphviz\bin` directory on your system (e.g., `C:\Graphviz\bin`).

3. **Prepare Input Logs:**
   - **Download Logs:** Download the process execution logs from the following link: [Dataset_files](https://drive.google.com/file/d/1DDP7OKQhD8cno2tbSpLlIPZ-Mh5y-XUC/view)
   - **Place Logs:** Place the downloaded logs in the `media/input` folder.
   - **(Optional)** Feel free to clean up all the folders on `media/output` and subfolders for not have to deal with my particular results.
4. **Configuration Files:**
   - **`option.dat`:** This file holds configuration parameters for the experiments. Modify it to adjust settings as needed.
   - **`Encoding.dat`:** This file specifies the type of index encoding to use (simple or complex).

5. **Run the Main Script:**
   ```bash
   python main.py
   ```

   The results will be generated and saved in the `media/output` folder.

6. **Frontend Interface (Optional):**
   - The `frontend` directory contains a Python script for a user-friendly interface to run experiments. However, be aware that not all features are fully functional yet (declarative button functionality is still under development).
   - To use the interface:
     ```bash
     cd frontend
     python Gui_runner.py
     ```

7. **Postprocessing (Optional):**
   - If you desire a more organized result structure:
     - After running the main script, use `src/file_verifier/reorganizer.py` to organize output folders.
     - Then, use `src/file_verifier/processinginpost.py` to scan all files and generate a summary of the data in the `media/postprocessing` folder.

**Project Inspiration:**

- Luca Boschiero's work ([https://github.com/lucaboschiero/tesi](https://github.com/lucaboschiero/tesi)) served as a foundational source for this project.

**Additional Considerations:**

- Ensure you have the necessary permissions to access the provided Google Drive link for downloading logs.
- Customize configuration parameters in `option.dat` to tailor experiments to your specific process and goals.