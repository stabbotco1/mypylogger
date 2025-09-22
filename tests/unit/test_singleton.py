"""
Tests for SingletonLogger class - singleton behavior and thread safety.
"""
import pytest
import logging
import threading
import time
from unittest.mock import patch, MagicMock

from mypylogger.core import SingletonLogger


class TestSingletonBehavior:
    """Test singleton pattern implementation."""
    
    def test_singleton_returns_same_instance(self, mock_logger_instance):
        """Test that multiple calls to constructor return same instance."""
        instance1 = SingletonLogger()
        instance2 = SingletonLogger()
        instance3 = SingletonLogger()
        
        assert instance1 is instance2
        assert instance2 is instance3
        assert instance1 is instance3
    
    def test_get_logger_returns_same_logger(self, mock_logger_instance):
        """Test that get_logger() returns the same logger instance."""
        logger1 = SingletonLogger.get_logger()
        logger2 = SingletonLogger.get_logger()
        logger3 = SingletonLogger.get_logger()
        
        assert logger1 is logger2
        assert logger2 is logger3
        assert logger1 is logger3
    
    def test_singleton_persists_across_modules(self, mock_logger_instance):
        """Test that singleton behavior works across different access patterns."""
        # Access via class
        instance1 = SingletonLogger()
        logger1 = instance1.get_logger()
        
        # Access via static method
        logger2 = SingletonLogger.get_logger()
        
        # Access via different instance
        instance2 = SingletonLogger()
        logger3 = instance2.get_logger()
        
        assert logger1 is logger2
        assert logger2 is logger3
        assert instance1 is instance2


class TestThreadSafety:
    """Test thread-safe singleton implementation."""
    
    def test_concurrent_singleton_creation(self, mock_logger_instance):
        """Test that concurrent access creates only one instance."""
        instances = []
        loggers = []
        barrier = threading.Barrier(5)  # Synchronize 5 threads
        
        def create_singleton():
            barrier.wait()  # Wait for all threads to be ready
            instance = SingletonLogger()
            logger = instance.get_logger()
            instances.append(instance)
            loggers.append(logger)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_singleton)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all instances are the same
        assert len(instances) == 5
        assert len(loggers) == 5
        
        first_instance = instances[0]
        first_logger = loggers[0]
        
        for instance in instances[1:]:
            assert instance is first_instance
        
        for logger in loggers[1:]:
            assert logger is first_logger
    
    def test_concurrent_get_logger_calls(self, mock_logger_instance):
        """Test that concurrent get_logger() calls are thread-safe."""
        loggers = []
        barrier = threading.Barrier(10)  # Synchronize 10 threads
        
        def get_logger():
            barrier.wait()  # Wait for all threads to be ready
            logger = SingletonLogger.get_logger()
            loggers.append(logger)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_logger)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all loggers are the same
        assert len(loggers) == 10
        first_logger = loggers[0]
        
        for logger in loggers[1:]:
            assert logger is first_logger
    
    def test_mixed_concurrent_access(self, mock_logger_instance):
        """Test mixed concurrent access patterns."""
        results = []
        barrier = threading.Barrier(8)  # Synchronize 8 threads
        
        def access_pattern_1():
            barrier.wait()
            instance = SingletonLogger()
            logger = instance.get_logger()
            results.append(('pattern1', instance, logger))
        
        def access_pattern_2():
            barrier.wait()
            logger = SingletonLogger.get_logger()
            instance = SingletonLogger()
            results.append(('pattern2', instance, logger))
        
        threads = []
        # Create 4 threads of each pattern
        for _ in range(4):
            threads.append(threading.Thread(target=access_pattern_1))
            threads.append(threading.Thread(target=access_pattern_2))
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all instances and loggers are the same
        assert len(results) == 8
        
        first_instance = results[0][1]
        first_logger = results[0][2]
        
        for pattern, instance, logger in results[1:]:
            assert instance is first_instance
            assert logger is first_logger


class TestLoggingLevelConstants:
    """Test logging level constants are properly exposed."""
    
    def test_logging_constants_exist(self):
        """Test that all logging constants are available."""
        assert hasattr(SingletonLogger, 'DEBUG')
        assert hasattr(SingletonLogger, 'INFO')
        assert hasattr(SingletonLogger, 'WARNING')
        assert hasattr(SingletonLogger, 'ERROR')
        assert hasattr(SingletonLogger, 'CRITICAL')
    
    def test_logging_constants_values(self):
        """Test that logging constants have correct values."""
        assert SingletonLogger.DEBUG == logging.DEBUG
        assert SingletonLogger.INFO == logging.INFO
        assert SingletonLogger.WARNING == logging.WARNING
        assert SingletonLogger.ERROR == logging.ERROR
        assert SingletonLogger.CRITICAL == logging.CRITICAL
    
    def test_constants_are_integers(self):
        """Test that all constants are integers."""
        assert isinstance(SingletonLogger.DEBUG, int)
        assert isinstance(SingletonLogger.INFO, int)
        assert isinstance(SingletonLogger.WARNING, int)
        assert isinstance(SingletonLogger.ERROR, int)
        assert isinstance(SingletonLogger.CRITICAL, int)


class TestGetEffectiveLevel:
    """Test get_effective_level method."""
    
    def test_get_effective_level_returns_int(self):
        """Test that get_effective_level returns an integer."""
        level = SingletonLogger.get_effective_level()
        assert isinstance(level, int)
        assert level >= 0
    
    def test_get_effective_level_static_method(self):
        """Test that get_effective_level can be called as static method."""
        level = SingletonLogger.get_effective_level()
        assert isinstance(level, int)
    
    def test_get_effective_level_instance_method(self, mock_logger_instance):
        """Test that get_effective_level works on instance."""
        instance = SingletonLogger()
        level = instance.get_effective_level()
        assert isinstance(level, int)


class TestLoggerConfiguration:
    """Test logger configuration and handler management."""
    
    def test_logger_uses_app_name_from_config(self, mock_logger_instance, clean_environment):
        """Test that logger uses app name from configuration."""
        import os
        os.environ['APP_NAME'] = 'test_app'
        
        logger = SingletonLogger.get_logger()
        assert logger.name == 'test_app'
    
    def test_logger_uses_default_app_name(self, mock_logger_instance, clean_environment):
        """Test that logger uses default app name when not configured."""
        logger = SingletonLogger.get_logger()
        assert logger.name == 'default_app'
    
    def test_logger_level_from_config(self, mock_logger_instance, clean_environment):
        """Test that logger level is set from configuration."""
        import os
        os.environ['LOG_LEVEL'] = 'DEBUG'
        
        logger = SingletonLogger.get_logger()
        assert logger.level == logging.DEBUG
    
    def test_logger_default_level(self, mock_logger_instance, clean_environment):
        """Test that logger uses default INFO level."""
        logger = SingletonLogger.get_logger()
        assert logger.level == logging.INFO
    
    def test_no_duplicate_handlers(self, mock_logger_instance, clean_environment):
        """Test that multiple calls don't add duplicate handlers."""
        logger1 = SingletonLogger.get_logger()
        initial_handler_count = len(logger1.handlers)
        
        logger2 = SingletonLogger.get_logger()
        logger3 = SingletonLogger.get_logger()
        
        assert logger1 is logger2
        assert logger2 is logger3
        assert len(logger2.handlers) == initial_handler_count
        assert len(logger3.handlers) == initial_handler_count
    
    def test_get_effective_level_matches_logger(self, mock_logger_instance, clean_environment):
        """Test that get_effective_level returns the logger's effective level."""
        import os
        os.environ['LOG_LEVEL'] = 'WARNING'
        
        logger = SingletonLogger.get_logger()
        effective_level = SingletonLogger.get_effective_level()
        
        assert effective_level == logger.getEffectiveLevel()
        assert effective_level == logging.WARNING


class TestConfigurationIntegration:
    """Test integration with configuration system."""
    
    def test_configuration_loaded_once(self, mock_logger_instance, clean_environment):
        """Test that configuration is loaded only once."""
        import os
        os.environ['APP_NAME'] = 'initial_app'
        
        logger1 = SingletonLogger.get_logger()
        assert logger1.name == 'initial_app'
        
        # Change environment variable
        os.environ['APP_NAME'] = 'changed_app'
        
        # Should still use the original configuration
        logger2 = SingletonLogger.get_logger()
        assert logger2.name == 'initial_app'
        assert logger1 is logger2
    
    def test_thread_safe_configuration_loading(self, mock_logger_instance, clean_environment):
        """Test that configuration loading is thread-safe."""
        import os
        import threading
        
        os.environ['APP_NAME'] = 'thread_test_app'
        os.environ['LOG_LEVEL'] = 'ERROR'
        
        loggers = []
        barrier = threading.Barrier(5)
        
        def get_configured_logger():
            barrier.wait()
            logger = SingletonLogger.get_logger()
            loggers.append(logger)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_configured_logger)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All loggers should be the same instance with same configuration
        assert len(loggers) == 5
        first_logger = loggers[0]
        
        for logger in loggers[1:]:
            assert logger is first_logger
            assert logger.name == 'thread_test_app'
            assert logger.level == logging.ERROR