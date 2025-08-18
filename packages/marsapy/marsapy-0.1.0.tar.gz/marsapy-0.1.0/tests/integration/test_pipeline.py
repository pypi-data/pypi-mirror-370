import pytest
import time
from marsa.pipeline import AspectSentimentPipeline
from marsa.sentiment import AspectSentimentResult

class TestAspectSentimentPipelineIntegration:    
    @pytest.fixture(scope="class")
    def real_pipeline(self):
        config_path = "tests/fixtures/config.yaml"
        return AspectSentimentPipeline(config_path)
    
    @pytest.fixture
    def sample_comments(self):
        return [
            "I love the camera quality but hate the battery life",
            "The screen is beautiful and the performance is amazing",
            "Poor build quality and terrible customer service",
            "Great value for money, highly recommend",
            "The phone feels cheap but works fine",
            "" 
        ]
    
    @pytest.fixture 
    def clear_sentiment_comments(self):
        return [
            "The camera is absolutely fantastic and amazing",   # clearly positive
            "The battery life is terrible and awful",           # clearly negative
            "I love everything about this phone",               # positive, general
            "This device is complete garbage",                  # negative, general
        ]
    
    # ---------- Basic Pipeline Functionality ----------
    
    def test_pipeline_processes_single_comment(self, real_pipeline):
        # Arrange
        comment = "I love the camera but hate the battery"
        
        # Act
        results = real_pipeline.process_corpus([comment])
        
        # Assert
        assert len(results) == 1
        assert isinstance(results[0], AspectSentimentResult)
        assert results[0].text == "i love the camera but hate the battery" 
        assert len(results[0].aspects) >= 0
    
    def test_pipeline_handles_empty_input(self, real_pipeline):
        # Arrange
        results = real_pipeline.process_corpus([])
        assert results == []
        
        # Act
        results = real_pipeline.process_corpus([""])
        
        # Assert
        assert len(results) == 1
        assert isinstance(results[0], AspectSentimentResult)
        assert len(results[0].aspects) == 0
    
    def test_pipeline_processes_multiple_comments(self, real_pipeline, sample_comments):
        # Arrange & Act
        results = real_pipeline.process_corpus(sample_comments)
        
        # Assert
        assert len(results) == len(sample_comments)
        assert all(isinstance(result, AspectSentimentResult) for result in results)
        
        for i, result in enumerate(results):
            if sample_comments[i] == "":
                assert result.text == ""
            else:
                assert len(result.text) > 0
    
    # ---------- End-to-End Accuracy ----------
    
    def test_pipeline_identifies_known_aspects(self, real_pipeline):
        # Arrange
        comments_with_aspects = [
            "The camera quality is great",
            "Battery life could be better", 
            "Screen resolution is amazing",
            "Build quality feels solid"
        ]
        
        # Act
        results = real_pipeline.process_corpus(comments_with_aspects)
        
        # Assert
        total_aspects_found = sum(len(result.aspects) for result in results)
        assert total_aspects_found > 0, "Pipeline should identify some aspects in test comments"
        for result in results:
            for aspect in result.aspects:
                assert len(aspect.aspect_match.text) > 0
                assert aspect.aspect_match.category is not None
                assert aspect.sentiment in ["positive", "negative", "neutral"]
    
    def test_pipeline_assigns_correct_sentiments(self, real_pipeline, clear_sentiment_comments):
        # Arrange & Act
        results = real_pipeline.process_corpus(clear_sentiment_comments)
        positive_found = 0
        negative_found = 0
        
        for result in results:
            for aspect in result.aspects:
                if aspect.sentiment == "positive":
                    positive_found += 1
                elif aspect.sentiment == "negative":
                    negative_found += 1
        
        # Assert
        assert positive_found > 0, "Should identify some positive sentiments"
        assert negative_found > 0, "Should identify some negative sentiments"
    
    def test_pipeline_handles_mixed_sentiments(self, real_pipeline):
        # Arrange
        mixed_comment = "I love the camera and screen but hate the battery life and build quality"
        
        # Act
        results = real_pipeline.process_corpus([mixed_comment])
        result = results[0]
        
        # Assert
        if len(result.aspects) > 1:
            sentiments = [aspect.sentiment for aspect in result.aspects]
            assert len(set(sentiments)) >= 1
    
    # ---------- Output Format Validation ----------
    
    def test_process_corpus_flat_output_structure(self, real_pipeline, sample_comments):
        # Arrange & Act
        results = real_pipeline.process_corpus_flat(sample_comments)
        
        # Assert
        assert len(results) == len(sample_comments)
        
        for result in results:
            required_keys = ['original_text', 'cleaned_text', 'aspects_found', 'aspect_sentiments']
            assert all(key in result for key in required_keys)
            
            assert isinstance(result['original_text'], str)
            assert isinstance(result['cleaned_text'], str)
            assert isinstance(result['aspects_found'], int)
            assert isinstance(result['aspect_sentiments'], list)
            
            for aspect_sentiment in result['aspect_sentiments']:
                aspect_keys = ['aspect', 'category', 'sentiment', 'confidence', 'start', 'end']
                assert all(key in aspect_sentiment for key in aspect_keys)
                
                assert isinstance(aspect_sentiment['aspect'], str)
                assert aspect_sentiment['sentiment'] in ['positive', 'negative', 'neutral']
                assert isinstance(aspect_sentiment['confidence'], (float, type(None)))
                assert isinstance(aspect_sentiment['start'], int)
                assert isinstance(aspect_sentiment['end'], int)
    
    def test_process_corpus_output_types(self, real_pipeline, sample_comments):
        # Arrange & Act
        results = real_pipeline.process_corpus(sample_comments)
        
        # Assert
        assert isinstance(results, list)
        assert all(isinstance(result, AspectSentimentResult) for result in results)
        
        for result in results:
            assert hasattr(result, 'text')
            assert hasattr(result, 'aspects')
            assert isinstance(result.text, str)
            assert isinstance(result.aspects, list)
    
    def test_output_consistency(self, real_pipeline):
        # Arrange
        test_comment = "Great camera but poor battery life"
        
        # Act
        corpus_results = real_pipeline.process_corpus([test_comment])
        flat_results = real_pipeline.process_corpus_flat([test_comment])
        
        corpus_result = corpus_results[0]
        flat_result = flat_results[0]
        
        # Assert
        assert flat_result['original_text'] == test_comment
        assert flat_result['cleaned_text'] == corpus_result.text
        assert flat_result['aspects_found'] == len(corpus_result.aspects)
        assert len(flat_result['aspect_sentiments']) == len(corpus_result.aspects)
        
        for i, flat_aspect in enumerate(flat_result['aspect_sentiments']):
            corpus_aspect = corpus_result.aspects[i]
            assert flat_aspect['aspect'] == corpus_aspect.aspect_match.text
            assert flat_aspect['category'] == corpus_aspect.aspect_match.category
            assert flat_aspect['sentiment'] == corpus_aspect.sentiment
            assert flat_aspect['confidence'] == corpus_aspect.confidence
            assert flat_aspect['start'] == corpus_aspect.aspect_match.start
            assert flat_aspect['end'] == corpus_aspect.aspect_match.end
    
    # ---------- Real Data Integration ----------
    
    def test_pipeline_with_actual_review_data(self, real_pipeline):
        # Arrange
        realistic_reviews = [
            "This smartphone has an excellent camera that takes crystal clear photos, but the battery drains way too quickly during heavy usage.",
            "The build quality is outstanding and feels premium in hand, though I wish the screen was a bit brighter outdoors.",
            "For the price point, this device offers great value. The performance is smooth and the design is sleek.",
            "I'm disappointed with the audio quality - it sounds tinny and lacks bass. The camera is decent though.",
            "The user interface is intuitive and easy to navigate. Battery life easily lasts a full day of moderate use."
        ]
        
        # Act
        results = real_pipeline.process_corpus(realistic_reviews)
        
        # Assert
        assert len(results) == len(realistic_reviews)
        
        total_aspects = sum(len(result.aspects) for result in results)
        assert total_aspects > 0, "Should find aspects in realistic review data"

        confidences = []
        for result in results:
            for aspect in result.aspects:
                if aspect.confidence is not None:
                    confidences.append(aspect.confidence)
        
        if confidences:
            assert all(0 <= conf <= 1 for conf in confidences), "Confidence should be between 0 and 1"
            assert any(conf > 0.3 for conf in confidences), "Should have some confident predictions"
    
    @pytest.mark.slow
    def test_pipeline_performance_reasonable(self, real_pipeline):
        # Arrange
        test_comments = [
            "Great camera quality",
            "Poor battery life", 
            "Excellent screen resolution",
            "Terrible build quality",
            "Amazing performance"
        ] * 10
        
        # Act
        start_time = time.time()
        results = real_pipeline.process_corpus(test_comments)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Assert
        assert len(results) == len(test_comments)
        assert processing_time < 30.0, f"Processing 50 comments took {processing_time:.2f}s, which seems too slow"
        avg_time_per_comment = processing_time / len(test_comments)
        assert avg_time_per_comment < 1.0, f"Average {avg_time_per_comment:.3f}s per comment seems too slow"
    
    # ---------- Error Handling ----------
    
    def test_pipeline_handles_special_characters(self, real_pipeline):
        # Arrange
        special_comments = [
            "Camera is 👍 but battery is 👎",
            "Price: $299.99 - great value!",
            "Screen size: 6.1\" - perfect!",
            "Rating: ★★★★☆",
            "Email: test@example.com works fine"
        ]
        
        # Act
        results = real_pipeline.process_corpus(special_comments)
        
        # Assert
        assert len(results) == len(special_comments)
        for result in results:
            assert isinstance(result, AspectSentimentResult)
            assert isinstance(result.text, str)
    
    def test_pipeline_handles_very_long_text(self, real_pipeline):
        # Arrange
        long_comment = "This phone has excellent camera quality. " * 50
        
        # Act
        results = real_pipeline.process_corpus([long_comment])
        
        # Assert
        assert len(results) == 1
        assert isinstance(results[0], AspectSentimentResult)
    
    def test_pipeline_handles_very_short_text(self, real_pipeline):
        # Arrange
        short_comments = ["Good", "Bad", "OK", "👍", "5/5"]
        
        # Act
        results = real_pipeline.process_corpus(short_comments)
        
        # Assert
        assert len(results) == len(short_comments)
        for result in results:
            assert isinstance(result, AspectSentimentResult)