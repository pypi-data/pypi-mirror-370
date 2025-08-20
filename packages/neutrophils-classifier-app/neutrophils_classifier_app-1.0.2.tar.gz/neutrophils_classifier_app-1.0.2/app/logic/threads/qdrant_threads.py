from PyQt5.QtCore import QThread, pyqtSignal
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Filter, FieldCondition, MatchAny
from tqdm import tqdm
import numpy as np

class QdrantFetchThread(QThread):
    """
    A thread to fetch embeddings from a Qdrant collection.
    """
    processing_complete = pyqtSignal(object, object)
    progress_update = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, host, port, collection_name, max_samples=1000, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.max_samples = max_samples
        self.is_running = True
        self.qdrant_client = QdrantClient(host=self.host, port=self.port)

    def run(self):
        """Fetch all labeled embeddings from the specified Qdrant collection."""
        try:
            print(f"Connecting to Qdrant at {self.host}:{self.port}...")
            print(f"Fetching labeled embeddings from collection: '{self.collection_name}'...")

            allowed_labels = ["M", "MM", "BN", "SN"]
            print(f"--> Restricting to labels: {allowed_labels}")

            scroll_filter = Filter(
                must=[
                    FieldCondition(
                        key="label",
                        match=MatchAny(any=allowed_labels)
                    )
                ]
            )

            total_points = self.qdrant_client.count(
                collection_name=self.collection_name,
                count_filter=scroll_filter,
                exact=True
            ).count

            if self.max_samples is not None:
                total_points = min(total_points, self.max_samples)

            print(f"Total points to fetch: {total_points}")

            all_points = []
            next_page_offset = None
            
            # Use a simple loop for progress reporting instead of tqdm in a thread
            fetched_count = 0
            while self.is_running:
                response, next_page_offset = self.qdrant_client.scroll(
                    collection_name=self.collection_name,
                    limit=250,
                    with_payload=True,
                    with_vectors=True,
                    offset=next_page_offset,
                    scroll_filter=scroll_filter,
                )
                all_points.extend(response)
                fetched_count += len(response)
                
                progress = int((fetched_count / total_points) * 100) if total_points > 0 else 100
                self.progress_update.emit(progress, f"Fetched {fetched_count} of {total_points} points")

                if next_page_offset is None or not self.is_running:
                    break

                if len(all_points) >= total_points:
                    all_points = all_points[:total_points]
                    break
            
            if not self.is_running:
                self.error_occurred.emit("Fetching cancelled.")
                return

            print(f"Fetched {len(all_points)} points from Qdrant collection '{self.collection_name}'.")
            
            if not all_points:
                self.error_occurred.emit("No points with a 'label' payload found in the collection.")
                return
                
            print(f"Successfully fetched {len(all_points)} labeled data points.")
            
            embeddings = np.array([point.vector for point in all_points])
            labels = [point.payload['label'] for point in all_points]
            
            self.processing_complete.emit(embeddings, labels)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False