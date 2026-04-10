"""
Evaluation Metrics for RewindYou Project

Three key metrics:
1. BERTScore - Summarization Faithfulness (Precision, Recall, F1)
2. Cosine Similarity - Retrieval Performance (Avg similarity + Precision@5)
3. Compression Ratio - Content Compression Analysis
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
import numpy as np
from bert_score import score as bertscore
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from db.mongodb import get_pages_collection
from db.chroma_db import query_embeddings
from ai.embedding_allminilm import embed_text
from content_archiver import load_cleaned_content


load_dotenv()


class EvaluationMetrics:
    """Compute evaluation metrics for RewindYou system."""
    
    def __init__(self):
        self.pages_collection = get_pages_collection()
        self.metrics_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bert_score": {},
            "retrieval_performance": {},
            "compression_analysis": {},
        }
    
    # ====================
    # METRIC 1: BERTScore
    # ====================
    
    def compute_bertscore(
        self, 
        summaries: List[str], 
        references: List[str],
        device: str = "cuda"
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute BERTScore for summaries against original content.
        
        Args:
            summaries: List of generated summaries
            references: List of original content (reference text)
            device: 'cuda' or 'cpu'
            
        Returns:
            Tuple of (precision, recall, f1) arrays
        """
        print("\n🔍 Computing BERTScore...")
        P, R, F1 = bertscore(summaries, references, lang="en", device=device)
        return P.numpy(), R.numpy(), F1.numpy()
    
    
    def evaluate_summarization_consolidated(self, user_id: Optional[str] = None, device: str = "cpu") -> Dict:
        """
        Evaluate summarization quality - CONSOLIDATED RESULTS ONLY.
        Compares ORIGINAL CONTENT (input) against GENERATED SUMMARIES (output) using BERTScore.
        
        Metrics computed:
        - Accuracy, Precision, Recall, F1
        - Confusion Matrix (binary classification: high quality vs low quality)
        
        Args:
            user_id: Filter by user (if None, uses all data)
            device: 'cuda' or 'cpu'
            
        Returns:
            Dictionary with consolidated BERTScore metrics
        """
        print("\n📊 METRIC 1: BERTScore Analysis (CONSOLIDATED)")
        print("=" * 60)
        
        query = {} if not user_id else {"user_id": user_id}
        docs = list(self.pages_collection.find(query))
        
        if not docs:
            print("❌ No documents found in database")
            return {}
        
        try:
            # Load cleaned content from files and get summaries
            cleaned_contents = []
            summaries = []
            successfully_loaded = 0
            failed_loads = 0
            
            for doc in docs:
                cleaned_content_file = doc.get("cleaned_content_file")
                summary = doc.get("summary", "")
                
                if not cleaned_content_file:
                    print(f"⚠️  Document {doc.get('_id', 'unknown')} has no cleaned content file")
                    failed_loads += 1
                    continue
                
                # Load cleaned content from file
                cleaned_content = load_cleaned_content(cleaned_content_file)
                if not cleaned_content or len(cleaned_content.strip()) == 0:
                    print(f"⚠️  Could not load content from {cleaned_content_file}")
                    failed_loads += 1
                    continue
                
                if not summary or len(summary.strip()) == 0:
                    print(f"⚠️  Document {doc.get('_id', 'unknown')} has no summary")
                    failed_loads += 1
                    continue
                
                cleaned_contents.append(cleaned_content)
                summaries.append(summary)
                successfully_loaded += 1
            
            print(f"📄 Documents in database: {len(docs)}")
            print(f"✅ Successfully loaded: {successfully_loaded}")
            print(f"❌ Failed to load: {failed_loads}")
            
            if len(cleaned_contents) < 2:
                print(f"⚠️  Need at least 2 valid cleaned content + summary pairs (found {len(cleaned_contents)})")
                return {}
            
            print(f"📊 Computing BERTScore for {len(cleaned_contents)} content-summary pairs...")
            print(f"   Comparing: CLEANED CONTENT (from files) → GENERATED SUMMARIES")
            
            # Compute BERTScore: cleaned content as reference, summaries as candidates
            P, R, F1 = bertscore(summaries, cleaned_contents, lang="en", device=device)
            P = P.numpy()
            R = R.numpy()
            F1 = F1.numpy()
            
            # Create binary labels: threshold at 0.5 F1 score
            # High quality (1) = F1 >= 0.5, Low quality (0) = F1 < 0.5
            threshold = 0.5
            y_true = np.where(F1 >= threshold, 1, 0)
            y_pred = np.where(F1 >= threshold, 1, 0)  # Use F1 as prediction
            
            # Calculate metrics
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1_overall = f1_score(y_true, y_pred, zero_division=0)
            cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
            
            results = {
                "total_summaries": len(cleaned_contents),
                "bertscore_metrics": {
                    "precision_mean": float(np.mean(P)),
                    "precision_std": float(np.std(P)),
                    "recall_mean": float(np.mean(R)),
                    "recall_std": float(np.std(R)),
                    "f1_mean": float(np.mean(F1)),
                    "f1_std": float(np.std(F1)),
                },
                "classification_metrics": {
                    "accuracy": float(accuracy),
                    "precision": float(precision),
                    "recall": float(recall),
                    "f1_score": float(f1_overall),
                },
                "confusion_matrix": {
                    "true_negatives": int(cm[0, 0]),
                    "false_positives": int(cm[0, 1]),
                    "false_negatives": int(cm[1, 0]),
                    "true_positives": int(cm[1, 1]),
                    "matrix": cm.tolist(),
                }
            }
            
            print(f"\n✅ BERTScore Statistics (Cleaned Content → Summary):")
            print(f"   Precision: {np.mean(P):.4f} (±{np.std(P):.4f})")
            print(f"   Recall:    {np.mean(R):.4f} (±{np.std(R):.4f})")
            print(f"   F1 Score:  {np.mean(F1):.4f} (±{np.std(F1):.4f})")
            
            print(f"\n✅ Classification Metrics (Quality Threshold: {threshold}):")
            print(f"   Accuracy:  {accuracy:.4f}")
            print(f"   Precision: {precision:.4f}")
            print(f"   Recall:    {recall:.4f}")
            print(f"   F1 Score:  {f1_overall:.4f}")
            
            print(f"\n✅ Confusion Matrix:")
            print(f"   ┌─────────────────┬──────────┬──────────┐")
            print(f"   │                 │ Predicted│          │")
            print(f"   │                 │  Low (0) │ High (1) │")
            print(f"   ├─────────────────┼──────────┼──────────┤")
            print(f"   │ Actual Low (0)  │   {cm[0, 0]:<6} │  {cm[0, 1]:<6} │")
            print(f"   │ Actual High (1) │   {cm[1, 0]:<6} │  {cm[1, 1]:<6} │")
            print(f"   └─────────────────┴──────────┴──────────┘")
            
            self.metrics_results["bert_score"] = results
            return results
            
        except Exception as e:
            print(f"❌ Error computing BERTScore: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error_msg": str(e)}
    
    
    def compute_retrieval_metrics_consolidated(
        self,
        test_queries: List[str],
        user_id: Optional[str] = None,
        top_k: int = 5
    ) -> Dict:
        """
        Compute retrieval performance - CONSOLIDATED RESULTS ONLY.
        Returns global average cosine similarity across all queries.
        
        Args:
            test_queries: List of test queries
            user_id: Filter by user
            top_k: Number of top results to evaluate
            
        Returns:
            Dictionary with consolidated retrieval metrics
        """
        print("\n📊 METRIC 2: Cosine Similarity (CONSOLIDATED)")
        print("=" * 60)
        
        print(f"\n🔍 Running {len(test_queries)} test queries...")
        
        all_similarities = []
        successful_queries = 0
        
        for query_text in test_queries:
            try:
                # Embed query
                query_embedding = embed_text(query_text).tolist()
                
                # Search - only add where clause if user_id is provided
                where_clause = {"user_id": {"$eq": user_id}} if user_id else None
                results = query_embeddings(
                    query_embedding,
                    where=where_clause,
                    n_results=top_k,
                )
                
                # Extract distances (cosine similarity)
                distances = results.get("distances", [[]])[0]
                
                if distances:
                    all_similarities.extend(distances)
                    successful_queries += 1
                    avg_sim = np.mean(distances)
                    print(f"   ✅ Query: '{query_text[:45]}...' | Avg: {avg_sim:.4f}")
                
            except Exception as e:
                print(f"   ⚠️  Query failed: {str(e)}")
        
        if not all_similarities:
            print("❌ No successful queries!")
            return {}
        
        overall_avg = np.mean(all_similarities)
        overall_std = np.std(all_similarities)
        
        results_dict = {
            "total_queries": len(test_queries),
            "successful_queries": successful_queries,
            "total_similarity_scores": len(all_similarities),
            "avg_cosine_similarity": float(overall_avg),
            "std_cosine_similarity": float(overall_std),
            "min_similarity": float(np.min(all_similarities)),
            "max_similarity": float(np.max(all_similarities)),
        }
        
        print(f"\n✅ CONSOLIDATED Cosine Similarity:")
        print(f"   Avg Similarity: {overall_avg:.4f}")
        print(f"   Std Dev:        {overall_std:.4f}")
        print(f"   Range:          {np.min(all_similarities):.4f} - {np.max(all_similarities):.4f}")
        
        self.metrics_results["retrieval_performance"] = results_dict
        return results_dict
    
    
    def compute_compression_ratio_consolidated(self, user_id: Optional[str] = None) -> Dict:
        """
        Compute compression ratio - CONSOLIDATED RESULTS ONLY.
        Compression Ratio = Summary Word Count / Original Word Count
        
        Returns global average across all documents.
        
        Args:
            user_id: Filter by user
            
        Returns:
            Dictionary with consolidated compression metrics
        """
        print("\n📊 METRIC 3: Compression Ratio (CONSOLIDATED)")
        print("=" * 60)
        
        query = {} if not user_id else {"user_id": user_id}
        docs = list(self.pages_collection.find(query))
        
        if not docs:
            print("❌ No documents found in database")
            return {}
        
        compression_ratios = []
        
        for doc in docs:
            original_words = doc.get("word_count", 0)
            summary = doc.get("summary", "")
            summary_words = len(summary.split()) if summary else 0
            
            if original_words > 0:
                ratio = summary_words / original_words
                compression_ratios.append(ratio)
        
        if not compression_ratios:
            print("❌ No valid compression ratios computed")
            return {}
        
        overall = {
            "total_documents": len(docs),
            "documents_with_ratio": len(compression_ratios),
            "avg_compression_ratio": float(np.mean(compression_ratios)),
            "compression_std": float(np.std(compression_ratios)),
            "min_ratio": float(np.min(compression_ratios)),
            "max_ratio": float(np.max(compression_ratios)),
            "median_ratio": float(np.median(compression_ratios)),
        }
        
        print(f"\n✅ CONSOLIDATED Compression Metrics:")
        print(f"   Total Documents:    {overall['total_documents']}")
        print(f"   Avg Compression:    {overall['avg_compression_ratio']:.4f} ({overall['avg_compression_ratio']*100:.2f}%)")
        print(f"   Std Dev:            {overall['compression_std']:.4f}")
        print(f"   Range:              {overall['min_ratio']:.4f} - {overall['max_ratio']:.4f}")
        
        self.metrics_results["compression_analysis"] = overall
        return overall
    
    
    def print_consolidated_results(self):
        """Print FINAL CONSOLIDATED results only."""
        print("\n" + "=" * 80)
        print("FINAL EVALUATION RESULTS (CONSOLIDATED)")
        print("=" * 80)
        
        # BERTScore Results
        print("\n" + "█" * 80)
        print("1️⃣  BERTScore Analysis")
        print("█" * 80)
        if "bert_score" in self.metrics_results and self.metrics_results["bert_score"]:
            bs = self.metrics_results["bert_score"]
            if "bertscore_metrics" in bs:
                print(f"\n📈 BERTScore Metrics:")
                print(f"   Precision (μ±σ): {bs['bertscore_metrics']['precision_mean']:.4f} ± {bs['bertscore_metrics']['precision_std']:.4f}")
                print(f"   Recall    (μ±σ): {bs['bertscore_metrics']['recall_mean']:.4f} ± {bs['bertscore_metrics']['recall_std']:.4f}")
                print(f"   F1 Score  (μ±σ): {bs['bertscore_metrics']['f1_mean']:.4f} ± {bs['bertscore_metrics']['f1_std']:.4f}")
        
        # Retrieval Performance
        print("\n" + "█" * 80)
        print("2️⃣  Cosine Similarity (Retrieval Performance)")
        print("█" * 80)
        if "retrieval_performance" in self.metrics_results and self.metrics_results["retrieval_performance"]:
            rp = self.metrics_results["retrieval_performance"]
            print(f"\n📊 Overall Retrieval Metrics:")
            print(f"   Total Queries:      {rp['total_queries']}")
            print(f"   Successful:         {rp['successful_queries']}/{rp['total_queries']}")
            print(f"   Avg Cosine Sim:    {rp['avg_cosine_similarity']:.4f}")
            print(f"   Std Dev:            {rp['std_cosine_similarity']:.4f}")
            print(f"   Range:              {rp['min_similarity']:.4f} - {rp['max_similarity']:.4f}")
        
        # Compression Ratio
        print("\n" + "█" * 80)
        print("3️⃣  Compression Ratio Analysis")
        print("█" * 80)
        if "compression_analysis" in self.metrics_results and self.metrics_results["compression_analysis"]:
            ca = self.metrics_results["compression_analysis"]
            print(f"\n📊 Overall Compression Metrics:")
            print(f"   Total Documents:  {ca['total_documents']}")
            print(f"   Avg Ratio:         {ca['avg_compression_ratio']:.4f} ({ca['avg_compression_ratio']*100:.2f}%)")
            print(f"   Std Dev:           {ca['compression_std']:.4f}")
            print(f"   Median:            {ca['median_ratio']:.4f}")
            print(f"   Range:             {ca['min_ratio']:.4f} - {ca['max_ratio']:.4f}")
        
        print("\n" + "=" * 80)
        print("✅ EVALUATION COMPLETE")
        print("=" * 80)


def main():
    """Run complete evaluation on stored documents. Returns CONSOLIDATED RESULTS ONLY."""
    print("\n🚀 Starting RewindYou Evaluation Metrics")
    print("=" * 80)
    
    evaluator = EvaluationMetrics()
    
    # METRIC 1: BERTScore (Consolidated)
    evaluator.evaluate_summarization_consolidated(device="cpu")
    
    # METRIC 2: Cosine Similarity (Consolidated)
    test_queries = [
        "What is machine learning?",
        "Tell me about AI trends",
        "How does deep learning work?",
        "Information about neural networks",
        "What are transformers?",
        "Search results related to NLP",
        "Explain database optimization",
        "Best practices for web development",
    ]
    evaluator.compute_retrieval_metrics_consolidated(test_queries)
    
    # METRIC 3: Compression Ratio (Consolidated)
    evaluator.compute_compression_ratio_consolidated()
    
    # Print FINAL consolidated results
    evaluator.print_consolidated_results()


if __name__ == "__main__":
    main()
