"""
QuickInsights - AI-Powered Data Insights Engine

Bu modül, yapay zeka kullanarak veri setlerinde otomatik pattern recognition,
anomaly detection ve intelligent insights sağlar.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import warnings

warnings.filterwarnings("ignore")

try:
    from sklearn.cluster import KMeans, DBSCAN, IsolationForest
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.decomposition import PCA
    from sklearn.feature_selection import SelectKBest, f_regression
    from sklearn.metrics import silhouette_score

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn bulunamadı. AI özellikleri sınırlı olacak.")

try:
    from scipy import stats

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️  scipy bulunamadı. İstatistiksel analizler sınırlı olacak.")


class AIInsightEngine:
    """
    AI destekli veri insights motoru

    Geleneksel istatistiksel yöntemlerin ötesine geçen yapay zeka tabanlı
    pattern recognition, anomaly detection ve intelligent insights sağlar.
    """

    def __init__(self, df: pd.DataFrame):
        """
        AIInsightEngine başlatıcısı

        Parameters
        ----------
        df : pd.DataFrame
            Analiz edilecek veri seti
        """
        self.df = df.copy()
        self.insights = {}
        self.patterns = {}
        self.anomalies = {}
        self.trends = {}

        # Veri tiplerini belirle
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        # AI modelleri için hazırlık
        self._prepare_data()

    def _prepare_data(self):
        """AI analizi için veriyi hazırlar"""
        # Sayısal verileri normalize et
        if len(self.numeric_cols) > 0:
            self.scaler = StandardScaler()
            self.df_scaled = pd.DataFrame(
                self.scaler.fit_transform(self.df[self.numeric_cols]),
                columns=self.numeric_cols,
                index=self.df.index,
            )

        # Kategorik verileri encode et
        self.label_encoders = {}
        self.df_encoded = self.df.copy()

        for col in self.categorical_cols:
            if self.df[col].nunique() < 100:  # Çok fazla unique değer varsa encode etme
                le = LabelEncoder()
                self.df_encoded[col] = le.fit_transform(self.df[col].astype(str))
                self.label_encoders[col] = le

    def discover_patterns(self, max_patterns: int = 10) -> Dict[str, Any]:
        """
        Veri setinde otomatik pattern discovery yapar

        Parameters
        ----------
        max_patterns : int
            Maksimum pattern sayısı

        Returns
        -------
        Dict[str, Any]
            Keşfedilen pattern'lar
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn bulunamadı"}

        patterns = {}

        # 1. Clustering Patterns
        if len(self.numeric_cols) >= 2:
            patterns["clustering"] = self._discover_clustering_patterns()

        # 2. Correlation Patterns
        if len(self.numeric_cols) >= 2:
            patterns["correlations"] = self._discover_correlation_patterns()

        # 3. Sequential Patterns
        if len(self.datetime_cols) > 0:
            patterns["sequential"] = self._discover_sequential_patterns()

        # 4. Categorical Patterns
        if len(self.categorical_cols) > 0:
            patterns["categorical"] = self._discover_categorical_patterns()

        # 5. Feature Importance Patterns
        if len(self.numeric_cols) >= 2:
            patterns["feature_importance"] = self._discover_feature_importance()

        self.patterns = patterns
        return patterns

    def _discover_clustering_patterns(self) -> Dict[str, Any]:
        """Clustering pattern'larını keşfeder"""
        patterns = {}

        # Optimal cluster sayısını bul
        if len(self.numeric_cols) >= 2:
            # PCA ile boyut azaltma
            pca = PCA(n_components=min(3, len(self.numeric_cols)))
            data_pca = pca.fit_transform(self.df_scaled)

            # K-means için optimal k bulma
            inertias = []
            silhouette_scores = []
            k_range = range(2, min(11, len(self.df) // 10))

            for k in k_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(data_pca)
                inertias.append(kmeans.inertia_)

                if k > 1:
                    silhouette_scores.append(silhouette_score(data_pca, kmeans.labels_))
                else:
                    silhouette_scores.append(0)

            # Elbow method ile optimal k
            optimal_k = k_range[np.argmax(silhouette_scores)]

            # Optimal clustering
            optimal_kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            optimal_kmeans.fit(data_pca)

            patterns["optimal_clusters"] = optimal_k
            patterns["cluster_labels"] = optimal_kmeans.labels_.tolist()
            patterns["silhouette_score"] = silhouette_score(
                data_pca, optimal_kmeans.labels_
            )
            patterns["explained_variance"] = pca.explained_variance_ratio_.tolist()

            # Cluster karakteristikleri
            cluster_centers = optimal_kmeans.cluster_centers_
            cluster_characteristics = []

            for i in range(optimal_k):
                cluster_mask = optimal_kmeans.labels_ == i
                cluster_data = self.df_scaled[cluster_mask]

                characteristics = {
                    "cluster_id": i,
                    "size": int(cluster_mask.sum()),
                    "percentage": float(cluster_mask.sum() / len(self.df) * 100),
                    "center": cluster_centers[i].tolist(),
                    "features": {},
                }

                # Her özellik için cluster karakteristikleri
                for j, col in enumerate(self.numeric_cols):
                    if j < len(cluster_centers[i]):
                        characteristics["features"][col] = {
                            "mean": float(cluster_data[col].mean()),
                            "std": float(cluster_data[col].std()),
                            "center_value": float(cluster_centers[i][j]),
                        }

                cluster_characteristics.append(characteristics)

            patterns["cluster_characteristics"] = cluster_characteristics

        return patterns

    def _discover_correlation_patterns(self) -> Dict[str, Any]:
        """Korelasyon pattern'larını keşfeder"""
        patterns = {}

        if len(self.numeric_cols) >= 2:
            # Pearson korelasyonu
            pearson_corr = self.df[self.numeric_cols].corr(method="pearson")

            # Spearman korelasyonu
            spearman_corr = self.df[self.numeric_cols].corr(method="spearman")

            # Güçlü korelasyonlar
            strong_correlations = []
            moderate_correlations = []

            for i in range(len(self.numeric_cols)):
                for j in range(i + 1, len(self.numeric_cols)):
                    col1, col2 = self.numeric_cols[i], self.numeric_cols[j]
                    pearson_val = pearson_corr.loc[col1, col2]
                    spearman_val = spearman_corr.loc[col1, col2]

                    correlation_info = {
                        "feature1": col1,
                        "feature2": col2,
                        "pearson": float(pearson_val),
                        "spearman": float(spearman_val),
                        "strength": (
                            "strong"
                            if abs(pearson_val) > 0.7
                            else "moderate"
                            if abs(pearson_val) > 0.3
                            else "weak"
                        ),
                    }

                    if abs(pearson_val) > 0.7:
                        strong_correlations.append(correlation_info)
                    elif abs(pearson_val) > 0.3:
                        moderate_correlations.append(correlation_info)

            patterns["strong_correlations"] = strong_correlations
            patterns["moderate_correlations"] = moderate_correlations
            patterns["pearson_matrix"] = pearson_corr.to_dict()
            patterns["spearman_matrix"] = spearman_corr.to_dict()

            # Non-linear relationships
            non_linear_patterns = self._discover_non_linear_patterns()
            patterns["non_linear_patterns"] = non_linear_patterns

        return patterns

    def _discover_non_linear_patterns(self) -> List[Dict[str, Any]]:
        """Non-linear pattern'ları keşfeder"""
        patterns = []

        if len(self.numeric_cols) >= 2:
            for i in range(len(self.numeric_cols)):
                for j in range(i + 1, len(self.numeric_cols)):
                    col1, col2 = self.numeric_cols[i], self.numeric_cols[j]

                    # Polynomial relationships
                    x = self.df[col1].values
                    y = self.df[col2].values

                    # 2nd degree polynomial fit
                    try:
                        coeffs = np.polyfit(x, y, 2)
                        y_pred = np.polyval(coeffs, x)
                        r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum(
                            (y - np.mean(y)) ** 2
                        )

                        if r_squared > 0.7:
                            patterns.append(
                                {
                                    "type": "polynomial",
                                    "feature1": col1,
                                    "feature2": col2,
                                    "degree": 2,
                                    "r_squared": float(r_squared),
                                    "coefficients": coeffs.tolist(),
                                }
                            )
                    except Exception as e:
                        print(f"⚠️  Linear pattern analizi hatası: {e}")
                        pass

                    # Exponential relationships
                    try:
                        # Log transformation
                        y_log = np.log(np.abs(y) + 1e-10)
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            x, y_log
                        )
                        r_squared = r_value**2

                        if r_squared > 0.7:
                            patterns.append(
                                {
                                    "type": "exponential",
                                    "feature1": col1,
                                    "feature2": col2,
                                    "r_squared": float(r_squared),
                                    "slope": float(slope),
                                    "intercept": float(intercept),
                                }
                            )
                    except Exception as e:
                        print(f"⚠️  Exponential pattern analizi hatası: {e}")
                        pass

        return patterns

    def _discover_sequential_patterns(self) -> Dict[str, Any]:
        """Zaman serisi pattern'larını keşfeder"""
        patterns = {}

        if len(self.datetime_cols) > 0 and len(self.numeric_cols) > 0:
            time_col = self.datetime_cols[0]

            for numeric_col in self.numeric_cols[:3]:  # İlk 3 sayısal sütun
                # Zaman serisi analizi
                time_series = self.df.set_index(time_col)[numeric_col].sort_index()

                # Trend analizi
                try:
                    x = np.arange(len(time_series))
                    y = time_series.values

                    # Linear trend
                    slope, intercept, _, _, _ = stats.linregress(x, y)
                    trend_strength = slope**2

                    # Seasonality detection (basit)
                    if len(time_series) > 12:
                        # Monthly seasonality
                        monthly_means = time_series.groupby(
                            time_series.index.month
                        ).mean()
                        seasonality_strength = (
                            monthly_means.std() / monthly_means.mean()
                        )

                        patterns[f"{numeric_col}_trend"] = {
                            "slope": float(slope),
                            "trend_strength": float(trend_strength),
                            "p_value": float(
                                0
                            ),  # linregress does not return p_value directly
                            "seasonality_strength": float(seasonality_strength),
                        }
                except Exception as e:
                    print(f"⚠️  Trend analizi hatası: {e}")
                    pass

        return patterns

    def _discover_categorical_patterns(self) -> Dict[str, Any]:
        """Kategorik pattern'ları keşfeder"""
        patterns = {}

        for col in self.categorical_cols:
            if col in self.label_encoders:
                # Value counts
                value_counts = self.df[col].value_counts()

                # Entropy calculation
                probabilities = value_counts / len(self.df)
                entropy = -np.sum(probabilities * np.log2(probabilities))

                patterns[col] = {
                    "unique_values": int(value_counts.nunique()),
                    "entropy": float(entropy),
                    "most_common": (
                        value_counts.index[0] if len(value_counts) > 0 else None
                    ),
                    "most_common_count": (
                        int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
                    ),
                    "distribution": value_counts.to_dict(),
                }

        # Cross-categorical patterns
        if len(self.categorical_cols) >= 2:
            cross_patterns = []

            for i in range(len(self.categorical_cols)):
                for j in range(i + 1, len(self.categorical_cols)):
                    col1, col2 = self.categorical_cols[i], self.categorical_cols[j]

                    # Contingency table
                    contingency = pd.crosstab(self.df[col1], self.df[col2])

                    # Chi-square test
                    try:
                        chi2, p_value, dof, expected = stats.chi2_contingency(
                            contingency
                        )

                        if p_value < 0.05:  # Significant relationship
                            cross_patterns.append(
                                {
                                    "feature1": col1,
                                    "feature2": col2,
                                    "chi2": float(chi2),
                                    "p_value": float(p_value),
                                    "significant": True,
                                    "contingency_table": contingency.to_dict(),
                                }
                            )
                    except Exception as e:
                        print(f"⚠️  Chi-square test hatası: {e}")
                        pass

            patterns["cross_categorical"] = cross_patterns

        return patterns

    def _discover_feature_importance(self) -> Dict[str, Any]:
        """Feature importance pattern'larını keşfeder"""
        patterns = {}

        if len(self.numeric_cols) >= 2:
            # Unsupervised feature importance (variance)
            variance_importance = self.df_scaled.var().sort_values(ascending=False)

            # Feature selection scores
            if len(self.numeric_cols) >= 3:
                try:
                    # F-regression scores (correlation with target)
                    # Use first numeric column as target for demonstration
                    target_col = self.numeric_cols[0]
                    feature_cols = self.numeric_cols[1:]

                    if len(feature_cols) > 0:
                        selector = SelectKBest(
                            score_func=f_regression, k=len(feature_cols)
                        )
                        X = self.df_scaled[feature_cols]
                        y = self.df_scaled[target_col]

                        selector.fit(X, y)
                        f_scores = selector.scores_
                        p_values = selector.pvalues_

                        feature_scores = []
                        for i, col in enumerate(feature_cols):
                            feature_scores.append(
                                {
                                    "feature": col,
                                    "f_score": float(f_scores[i]),
                                    "p_value": float(p_values[i]),
                                    "significant": p_values[i] < 0.05,
                                }
                            )

                        # Sort by f_score
                        feature_scores.sort(key=lambda x: x["f_score"], reverse=True)

                        patterns["feature_selection"] = {
                            "target": target_col,
                            "feature_scores": feature_scores,
                            "top_features": [f["feature"] for f in feature_scores[:5]],
                        }
                except Exception as e:
                    print(f"⚠️  Feature selection hatası: {e}")
                    pass

            patterns["variance_importance"] = variance_importance.to_dict()

        return patterns

    def detect_anomalies(
        self, method: str = "auto", contamination: float = 0.1
    ) -> Dict[str, Any]:
        """
        Veri setinde anomalileri tespit eder

        Parameters
        ----------
        method : str
            Anomali tespit yöntemi ('auto', 'isolation_forest', 'dbscan', 'statistical')
        contamination : float
            Beklenen anomali oranı

        Returns
        -------
        Dict[str, Any]
            Tespit edilen anomaliler
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn bulunamadı"}

        anomalies = {}

        if method == "auto":
            # Birden fazla yöntem dene
            methods = ["isolation_forest", "dbscan", "statistical"]
        else:
            methods = [method]

        for method_name in methods:
            try:
                if method_name == "isolation_forest":
                    anomalies[method_name] = self._detect_anomalies_isolation_forest(
                        contamination
                    )
                elif method_name == "dbscan":
                    anomalies[method_name] = self._detect_anomalies_dbscan()
                elif method_name == "statistical":
                    anomalies[method_name] = self._detect_anomalies_statistical()
            except Exception as e:
                anomalies[method_name] = {"error": str(e)}

        # En iyi yöntemi seç
        if (
            "isolation_forest" in anomalies
            and "error" not in anomalies["isolation_forest"]
        ):
            best_method = "isolation_forest"
        elif "dbscan" in anomalies and "error" not in anomalies["dbscan"]:
            best_method = "dbscan"
        else:
            best_method = "statistical"

        anomalies["best_method"] = best_method
        anomalies["best_results"] = anomalies.get(best_method, {})

        self.anomalies = anomalies
        return anomalies

    def _detect_anomalies_isolation_forest(
        self, contamination: float
    ) -> Dict[str, Any]:
        """Isolation Forest ile anomali tespiti"""
        if len(self.numeric_cols) < 2:
            return {"error": "En az 2 sayısal sütun gerekli"}

        # PCA ile boyut azaltma
        pca = PCA(n_components=min(10, len(self.numeric_cols)))
        data_pca = pca.fit_transform(self.df_scaled)

        # Isolation Forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        anomaly_labels = iso_forest.fit_predict(data_pca)

        # Anomalileri bul
        anomaly_indices = np.where(anomaly_labels == -1)[0]
        normal_indices = np.where(anomaly_labels == 1)[0]

        return {
            "anomaly_count": int(len(anomaly_indices)),
            "anomaly_percentage": float(len(anomaly_indices) / len(self.df) * 100),
            "anomaly_indices": anomaly_indices.tolist(),
            "normal_indices": normal_indices.tolist(),
            "anomaly_scores": iso_forest.decision_function(data_pca).tolist(),
            "explained_variance": pca.explained_variance_ratio_.tolist(),
        }

    def _detect_anomalies_dbscan(self) -> Dict[str, Any]:
        """DBSCAN ile anomali tespiti"""
        if len(self.numeric_cols) < 2:
            return {"error": "En az 2 sayısal sütun gerekli"}

        # PCA ile boyut azaltma
        pca = PCA(n_components=min(5, len(self.numeric_cols)))
        data_pca = pca.fit_transform(self.df_scaled)

        # DBSCAN
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        cluster_labels = dbscan.fit_predict(data_pca)

        # Noise points (-1) anomalilerdir
        anomaly_indices = np.where(cluster_labels == -1)[0]
        normal_indices = np.where(cluster_labels != -1)[0]

        return {
            "anomaly_count": int(len(anomaly_indices)),
            "anomaly_percentage": float(len(anomaly_indices) / len(self.df) * 100),
            "anomaly_indices": anomaly_indices.tolist(),
            "normal_indices": normal_indices.tolist(),
            "cluster_count": int(
                len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
            ),
            "explained_variance": pca.explained_variance_ratio_.tolist(),
        }

    def _detect_anomalies_statistical(self) -> Dict[str, Any]:
        """İstatistiksel yöntemlerle anomali tespiti"""
        anomalies = {}

        for col in self.numeric_cols:
            # Z-score method
            z_scores = np.abs(stats.zscore(self.df[col]))
            z_anomalies = np.where(z_scores > 3)[0]

            # IQR method
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            iqr_anomalies = np.where(
                (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            )[0]

            anomalies[col] = {
                "z_score_anomalies": z_anomalies.tolist(),
                "z_score_count": int(len(z_anomalies)),
                "iqr_anomalies": iqr_anomalies.tolist(),
                "iqr_count": int(len(iqr_anomalies)),
                "iqr_bounds": {
                    "lower": float(lower_bound),
                    "upper": float(upper_bound),
                },
            }

        return anomalies

    def predict_trends(self, target_col: str, horizon: int = 5) -> Dict[str, Any]:
        """
        Hedef değişken için trend tahmini yapar

        Parameters
        ----------
        target_col : str
            Tahmin edilecek hedef sütun
        horizon : int
            Tahmin ufku (kaç adım ileri)

        Returns
        -------
        Dict[str, Any]
            Trend tahminleri
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn bulunamadı"}

        if target_col not in self.numeric_cols:
            return {"error": f"{target_col} sayısal bir sütun değil"}

        trends = {}

        try:
            # Feature preparation
            feature_cols = [col for col in self.numeric_cols if col != target_col]

            if len(feature_cols) == 0:
                return {"error": "Tahmin için yeterli feature yok"}

            X = self.df_scaled[feature_cols]
            y = self.df_scaled[target_col]

            # Multiple models
            models = {
                "random_forest": RandomForestRegressor(
                    n_estimators=100, random_state=42
                ),
            }

            model_results = {}

            for model_name, model in models.items():
                # Train model
                model.fit(X, y)

                # Predictions
                y_pred = model.predict(X)

                # Model performance
                r_squared = model.score(X, y)
                mse = np.mean((y - y_pred) ** 2)

                # Feature importance
                if hasattr(model, "feature_importances_"):
                    feature_importance = dict(
                        zip(feature_cols, model.feature_importances_)
                    )
                elif hasattr(model, "coef_"):
                    feature_importance = dict(zip(feature_cols, model.coef_))
                else:
                    feature_importance = {}

                model_results[model_name] = {
                    "r_squared": float(r_squared),
                    "mse": float(mse),
                    "feature_importance": feature_importance,
                    "predictions": y_pred.tolist(),
                }

            # Best model selection
            best_model = max(
                model_results.keys(), key=lambda x: model_results[x]["r_squared"]
            )

            trends["models"] = model_results
            trends["best_model"] = best_model
            trends["best_performance"] = model_results[best_model]

            # Future predictions (basit extrapolation)
            if len(self.df) > horizon:
                # Son birkaç veri noktasından trend extrapolation
                recent_data = self.df[target_col].tail(horizon).values
                x = np.arange(len(recent_data))

                # Linear trend
                slope, intercept, _, _, _ = stats.linregress(x, recent_data)

                # Future predictions
                future_x = np.arange(len(recent_data), len(recent_data) + horizon)
                future_predictions = slope * future_x + intercept

                trends["future_predictions"] = {
                    "horizon": horizon,
                    "slope": float(slope),
                    "intercept": float(intercept),
                    "predictions": future_predictions.tolist(),
                    "trend_direction": "increasing" if slope > 0 else "decreasing",
                }

        except Exception as e:
            trends["error"] = str(e)

        self.trends = trends
        return trends

    def generate_insights_report(self) -> Dict[str, Any]:
        """
        Kapsamlı insights raporu oluşturur

        Returns
        -------
        Dict[str, Any]
            Insights raporu
        """
        report = {
            "summary": {
                "total_rows": len(self.df),
                "total_columns": len(self.df.columns),
                "numeric_columns": len(self.numeric_cols),
                "categorical_columns": len(self.categorical_cols),
                "datetime_columns": len(self.datetime_cols),
            },
            "patterns": self.patterns,
            "anomalies": self.anomalies,
            "trends": self.trends,
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Otomatik öneriler oluşturur"""
        recommendations = []

        # Data quality recommendations
        missing_percentage = (
            self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns)) * 100
        )
        if missing_percentage > 10:
            recommendations.append(
                f"Veri setinde %{missing_percentage:.1f} eksik değer var. Data cleaning önerilir."
            )

        # Feature engineering recommendations
        if len(self.numeric_cols) >= 3:
            recommendations.append(
                "Çoklu sayısal değişkenler mevcut. Feature interaction'ları oluşturulabilir."
            )

        # Anomaly detection recommendations
        if "anomalies" in self.insights:
            anomaly_count = sum(
                len(anom.get("anomaly_indices", []))
                for anom in self.anomalies.values()
                if isinstance(anom, dict) and "anomaly_indices" in anom
            )
            if anomaly_count > 0:
                recommendations.append(
                    f"{anomaly_count} anomali tespit edildi. Detaylı inceleme önerilir."
                )

        # Clustering recommendations
        if "patterns" in self.insights and "clustering" in self.insights["patterns"]:
            cluster_count = self.insights["patterns"]["clustering"].get(
                "optimal_clusters", 0
            )
            if cluster_count > 1:
                recommendations.append(
                    f"{cluster_count} doğal cluster tespit edildi. Segmentasyon analizi yapılabilir."
                )

        # Correlation recommendations
        if "patterns" in self.insights and "correlations" in self.insights["patterns"]:
            strong_corr_count = len(
                self.insights["patterns"]["correlations"].get("strong_correlations", [])
            )
            if strong_corr_count > 0:
                recommendations.append(
                    f"{strong_corr_count} güçlü korelasyon tespit edildi. Multicollinearity kontrol edilmeli."
                )

        return recommendations


def auto_ai_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Otomatik AI analizi yapar

    Parameters
    ----------
    df : pd.DataFrame
        Analiz edilecek veri seti

    Returns
    -------
    Dict[str, Any]
        AI analiz sonuçları
    """
    engine = AIInsightEngine(df)

    # Pattern discovery
    patterns = engine.discover_patterns()

    # Anomaly detection
    anomalies = engine.detect_anomalies()

    # Trend prediction (ilk sayısal sütun için)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    trends = {}
    if len(numeric_cols) > 0:
        trends = engine.predict_trends(numeric_cols[0])

    # Comprehensive report
    report = engine.generate_insights_report()

    return {
        "patterns": patterns,
        "anomalies": anomalies,
        "trends": trends,
        "report": report,
    }
